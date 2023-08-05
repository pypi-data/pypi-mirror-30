"""
Build a structural model of a wind turbine using mbwind
"""

import os
import itertools
import numpy as np
from numpy import dot, pi
from whales.rotor import Rotor
from mbwind.utils import rotmat_x, rotmat_y
from mbwind import (System, FreeJoint, RigidBody, RigidConnection, Hinge,
                    DistalModalElementFromFE, ModalElementFromFE)
from pybladed.blade import Tower
# from mbwind.old_io import load_modes_from_Bladed
from mbwind import LinearisedSystem
from beamfe import BeamFE, interleave
from bem import Blade


# Helpers for dealing with dof indices
def free_dof_indices(system, element):
    """Return DOF numbers for all free strains of ``element``"""
    def iterfunc():
        try:
            for istrain in itertools.count():
                yield system.dof_index(element, istrain)
        except (IndexError, ValueError):
            return  # run out of strains, or strain was prescribed
    return list(iterfunc())


def build_tower_model(s, basepath):
    if 'definition' in s['tower']:
        if 'mass' in s['tower']:
            raise ValueError("Both tower definition and explicit mass!")

        tower_filename = s['tower']['definition']
        if basepath:
            tower_filename = os.path.join(basepath, tower_filename)
        tower_definition = Tower(tower_filename)

        assert np.all(tower_definition.stn_pos[:, :2] == 0)  # vert.
        z_tower = tower_definition.stn_pos[:, 2]
        tower_fe = BeamFE(z_tower - z_tower[0],
                          tower_definition.density,
                          EA=1,
                          EIy=tower_definition.EIy,
                          EIz=tower_definition.EIz)
        tower_fe.set_boundary_conditions('C', 'C')
    else:
        tower_definition = None
        tower_fe = None

    return tower_definition, tower_fe


def build_blade_model(s, blade, basepath):
    if blade:
        root_length = s['rotor']['root length']
        blade_fe = build_fe_model(blade, root_length)
    else:
        blade = None
        blade_fe = None

    return blade, blade_fe


def build_fe_model(blade, root_length):
    # Calculate centrifugal force
    X0 = interleave(root_length + blade.x, 6)
    N = BeamFE.centrifugal_force_distribution(X0, blade.density)

    # Make FE model. FE twist is in geometric sense, negative to convention.
    # Calculate centrifugal stiffening for unit angular velocity, scale later.
    fe = BeamFE(blade.x, blade.density, blade.EA, blade.EI_flap,
                blade.EI_edge, twist=-blade.twist,
                axial_force=N)
    fe.set_boundary_conditions('C', 'F')

    return fe


class FloatingTurbineStructure(object):
    def __init__(self, structure_config, blade, modes_spin=None, gravity=9.81,
                 basepath=None):
        s = structure_config

        # Load flexible element definitions
        self.tower_definition, self.tower_fe = build_tower_model(s, basepath)
        self.blade_definition, self.blade_fe = build_blade_model(s, blade,
                                                                 basepath)

        # Create the elements

        # Free joint represents the rigid-body motion of the platform
        free_joint = FreeJoint('base')

        # This is the rigid-body mass of the platform structure
        conn_platform = RigidConnection('conn-platform',
                                        offset=s['platform']['CoM'])
        platform = RigidBody('platform',
                             mass=s['platform']['mass'],
                             inertia=np.diag(s['platform']['inertia']))
        free_joint.add_leaf(conn_platform)
        conn_platform.add_leaf(platform)

        # Flexible tower or equivalent rigid body
        if self.tower_fe:
            # move base of tower 10m up, and rotate so tower x-axis is vertical
            z_base = self.tower_definition.stn_pos[0, 2]
            conn_tower = RigidConnection('conn-tower', offset=[0, 0, z_base],
                                         rotation=rotmat_y(-pi/2))
            num_tower_modes = s['tower']['number of normal modes']
            tower = DistalModalElementFromFE(
                'tower', self.tower_fe, num_modes=num_tower_modes,
                damping=s['tower']['modal damping'])
        else:
            # move tower to COG
            conn_tower = RigidConnection(
                'conn-tower', offset=s['tower']['CoM'])
            tower = RigidBody('tower', s['tower']['mass'],
                              np.diag(s['tower']['inertia']))
        free_joint.add_leaf(conn_tower)
        conn_tower.add_leaf(tower)

        # The nacelle -- rigid body
        # rotate back so nacelle inertia is aligned with global coordinates
        if self.tower_fe:
            nacoff = s['nacelle']['offset from tower top']
            conn_nacelle = RigidConnection('conn-nacelle',
                                           offset=dot(rotmat_y(pi/2), nacoff),
                                           rotation=rotmat_y(pi/2))
            tower.add_leaf(conn_nacelle)
        else:
            conn_nacelle = RigidConnection(
                'conn-nacelle',
                offset=np.array([0, 0, s['nacelle']['height']]))
            free_joint.add_leaf(conn_nacelle)
        nacelle = RigidBody(
            'nacelle',
            mass=s['nacelle']['mass'],
            inertia=np.diag(s['nacelle'].get('inertia', np.zeros(3))))
        conn_nacelle.add_leaf(nacelle)

        # The rotor hub -- currently just connections (no mass)
        # rotate so rotor centre is aligned with global coordinates
        if self.tower_fe:
            rotoff = s['rotor']['offset from tower top']
            conn_rotor = RigidConnection('conn-rotor',
                                         offset=dot(rotmat_y(pi/2), rotoff),
                                         rotation=rotmat_y(pi/2))
            tower.add_leaf(conn_rotor)
            self.hub_height = (self.tower_definition.stn_pos[-1, 2] +
                               rotoff[-2])
        else:
            conn_rotor = RigidConnection(
                'conn-rotor',
                offset=np.array([0, 0, s['nacelle']['height']]))
            free_joint.add_leaf(conn_rotor)
            self.hub_height = s['nacelle']['height']

        # The drive shaft rotation (rotation about x)
        shaft = Hinge('shaft', [1, 0, 0])
        conn_rotor.add_leaf(shaft)

        # Hub inertia
        if 'hub mass' in s['rotor'] and 'hub inertia' in s['rotor']:
            hub = RigidBody('hub', s['rotor']['hub mass'],
                            np.diag([s['rotor']['hub inertia'], 0, 0]))
            shaft.add_leaf(hub)

        # The blades
        if self.blade_fe:
            rtlen = s['rotor']['root length']
            modal_damping = s['blade']['modal damping']
            self.rotor = Rotor(3, rtlen, self.blade_fe,
                               num_modes=s['blade']['num modes'],
                               damping=modal_damping,
                               modes_spin=modes_spin, pitch=True)
            self.rotor.connect_to(shaft)
        else:
            self.rotor = None
            rotor_body = RigidBody('rotor', s['rotor']['mass'],
                                   np.diag(s['rotor']['inertia']))
            shaft.add_leaf(rotor_body)

        # Build system
        self.system = System(gravity=gravity)
        self.system.add_leaf(free_joint)
        self.system.setup()

        if self.rotor:
            for b in self.rotor.pitch_bearings:
                self.system.prescribe(b, acc=0)

        # Constrain missing DOFs -- tower torsion & extension not complete
        # if self.tower_fe:
        #     self.system.prescribe(tower, part=[0, 3])

    def set_rigid(self, what):
        if what in ('tower', 'all'):
            self.system.prescribe(self.system.elements['tower'])
        if what in ('rotor', 'all'):
            for i in range(3):
                self.system.prescribe(self.system.elements['blade%d' % (i+1)])

    def set_flexible(self, what):
        if what in ('tower', 'all'):
            self.system.free(self.system.elements['tower'])
            # # Constrain missing DOFs -- tower torsion & extension not complete
            # self.system.prescribe(self.system.elements['tower'], part=[0, 3])
        if what in ('rotor', 'all'):
            for i in range(3):
                self.system.free(self.system.elements['blade%d' % (i+1)])

    def set_shaft_lock(self, locked):
        if locked:
            self.system.prescribe(self.system.elements['shaft'])
        else:
            self.system.free(self.system.elements['shaft'])

    def linearised_system(self, z0=None, zd0=None, mbc=False,
                          rotor_speed=None, azimuth=0, perturbation=None):

        # Linearise the system about the given operating point
        self.system.update_kinematics()
        linsys = LinearisedSystem.from_system(self.system, z0=z0, zd0=zd0,
                                              perturbation=perturbation)

        # Apply multi-blade coordinate transform if needed
        if mbc:
            assert rotor_speed is not None
            iblades = [free_dof_indices(self.system, 'blade{}'.format(i+1))
                       for i in range(3)]
            if mbc == 2:
                linsys = linsys.multiblade_transform2((azimuth, rotor_speed),
                                                      iblades)
            else:
                linsys = linsys.multiblade_transform((azimuth, rotor_speed),
                                                     iblades)

        return linsys

    def linearised_matrices(self, *args, **kwargs):
        linsys = self.linearised_system(*args, **kwargs)
        return linsys.M, linsys.C, linsys.K

    def describe_states(self):
        q = self.system.q
        states = [(q.owners[j], i) for i, j in enumerate(q.dofs.subset)]
        for owner, owner_states in itertools.groupby(states, lambda x: x[0]):
            numbers = [x[1] for x in owner_states]
            print('{:2}-{:2}: {}'.format(numbers[0], numbers[-1], owner))
