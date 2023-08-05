"""
Put together structural and BEM models
Rick Lupton
22 Jan 2014
"""

import os.path
import yaml

import numpy as np
from numpy import array
from scipy.misc import derivative

import mbwind
from mbwind import System, Hinge, LinearisedSystem, ReducedSystem

from whales.rotor import Rotor
from bem import BEMModel, AerofoilDatabase, Blade

from beamfe import BeamFE, interleave


def build_bem_model(blade, root_length, aerofoil_database):
    # Create BEM model, interpolating to same output radii as Bladed
    model = BEMModel(blade, root_length, num_blades=3,
                     aerofoil_database=aerofoil_database)
    return model


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


def build_structural_system(root_length, fe, num_modes, modal_damping,
                            rotor_speed, hub_mass_inertia=None):
    # Rotor speed is needed for centrifugal stiffening calculation.
    rotor = Rotor(3, root_length, fe, num_modes, modal_damping,
                  rotor_speed, pitch=True)
    system = System()
    shaft = Hinge('shaft', [1, 0, 0])
    rotor.connect_to(shaft)
    system.add_leaf(shaft)

    if hub_mass_inertia is not None:
        hub_mass, hub_inertia = hub_mass_inertia
        hub = mbwind.RigidBody('hub', hub_mass, np.diag([hub_inertia, 0, 0]))
        shaft.add_leaf(hub)

    system.setup()
    for b in rotor.pitch_bearings:
        system.prescribe(b, acc=0)
    return rotor, system


def perturb_vector(x, i, delta):
    """Perturb ith element of x by i"""
    y = x.copy()
    y[i] += delta
    return y


class AeroelasticModel:
    def __init__(self, blade_definition, aerofoil_database,
                 root_length, num_modes, fe_rotor_speed,
                 modal_damping, hub_mass_inertia=None,
                 dynamic_wake=False):
        """Build an aeroelastic model with FE, BEM and mbwind.

        Parameters
        ----------
        blade_definition: Blade object
            object containing details of the blade.
        aerofoil_database: AerofoilDatabase instance
        root_length: float
            distance from the rotation axis to the start of the blade
        num_modes: int
            number of modes to use in the modal representation
        fe_rotor_speed: float
            rotor speed used for calculating centrifugal stiffening in the FE
        modal_damping: float or array
            modal damping value[s]
        dynamic_wake: bool
            whether to calculate wake dynamics. Default is true.
        """
        self.blade = blade_definition
        self.root_length = root_length
        self.air_density = 1.225
        self.dynamic_wake = dynamic_wake

        self.fe = build_fe_model(blade_definition, root_length)
        self.bem = build_bem_model(blade_definition, root_length,
                                   aerofoil_database)
        self.rotor, self.system = build_structural_system(
            root_length, self.fe, num_modes, modal_damping,
            fe_rotor_speed, hub_mass_inertia)
        self.system.update_kinematics()

    @classmethod
    def from_yaml(cls, filename, fe_rotor_speed):
        # Read the data
        with open(filename) as f:
            config = yaml.safe_load(f)

        cs = config['structure']
        ca = config['aerodynamics']
        basepath = os.path.dirname(filename)

        # Load blade definition and aerofoil database
        blade = Blade.from_yaml(
            os.path.join(basepath, cs['blade']['definition']))

        min_spacing = cs['blade'].get('minimum station spacing')
        if min_spacing:
            new_x = [blade.x[0]]
            for xi in blade.x[1:]:
                if xi - new_x[-1] > min_spacing:
                    new_x.append(xi)
            blade = blade.resample(new_x)

        aerofoil_database = AerofoilDatabase(
            os.path.join(basepath, ca['aerofoil database']))

        if 'hub mass' in cs['rotor'] and 'hub inertia' in cs['rotor']:
            hub_mass_inertia = (cs['rotor']['hub mass'],
                                cs['rotor']['hub inertia'])
        else:
            hub_mass_inertia = None

        model = cls(blade, aerofoil_database,
                    cs['rotor']['root length'],
                    cs['blade']['num modes'],
                    fe_rotor_speed,
                    cs['blade']['modal damping'],
                    hub_mass_inertia)
        model._config = config
        return model

    @property
    def rotor_inertia(self):
        self.system.update_kinematics()
        rsys = ReducedSystem(self.system)
        return rsys.M[0, 0]

    def prescribe_rotor_speed(self, rotor_speed):
        shaft = self.system.elements['shaft']
        self.rotor_speed = rotor_speed
        self.system.prescribe(shaft, acc=0)

    def prescribe_rigid_blades(self):
        for b in self.rotor.blades:
            self.system.prescribe(b, acc=0)

    def plot_system(self):
        from mbwind.visual import SystemView
        from matplotlib.pyplot import subplots
        fig, ax = subplots(2, 2, figsize=(8, 8),
                           subplot_kw=dict(aspect=1), sharex=True,
                           sharey=True)
        axes = [ax[0, 1], ax[1, 0], ax[1, 1]]
        views = [SystemView(a, direction, self.system)
                 for a, direction in zip(axes, ['yx', 'xz', 'yz'])]
        ax[1, 1].set_xlabel('Y')
        ax[1, 0].set_ylabel('Z')
        ax[1, 0].set_xlabel('X')
        ax[0, 1].set_ylabel('X')
        for v in views:
            v.update()
            ax[0, 0].set_xlim(-6, 6)
            ax[0, 0].set_ylim(-6, 6)
        return fig

    def _aerostates2factors(self, states, wind_speed, rotor_speed):
        ul = states[0::2]
        ut = states[1::2]
        al = ul / wind_speed
        at = ut / rotor_speed / self.bem.radii
        return np.c_[al, at]

    def _factors2aerostates(self, factors, wind_speed, rotor_speed):
        q_aero = np.zeros(2 * factors.shape[0])
        q_aero[0::2] = factors[:, 0] * wind_speed
        q_aero[1::2] = factors[:, 1] * rotor_speed * self.bem.radii
        return q_aero

    def update_states(self, inputs, q_aero, q_struct):
        # Update structural system states
        self.system.set_state(q_struct)

        # Update aerodynamic loading
        loading = self.get_aerodynamic_loading(inputs, q_aero, q_struct)
        for i, b in enumerate(self.rotor.blades):
            b.loading = loading[i, :, :]
        self.system.update_kinematics()

    def get_aerodynamic_loading(self, inputs, q_aero, q_struct):
        wind_speed, rotor_speed, pitch = inputs
        factors = self._aerostates2factors(q_aero, wind_speed, rotor_speed)

        def loading_on_blade(b):
            # Blade velocities -- ignore axial velocity
            bvel = self.rotor.transform_blade_to_aero(
                b.elastic_velocities(), pitch)
            bvel_factors = bvel[:, 0:2] / wind_speed

            # Distributed forces (transformed into element coordinates)
            aero_forces = np.zeros_like(bvel)
            aero_forces[:, 0:2] = self.bem.forces(wind_speed, rotor_speed,
                                                  pitch, self.air_density,
                                                  factors, bvel_factors)
            beam_forces = self.rotor.transform_aero_to_blade(
                aero_forces, pitch)
            return beam_forces

        return np.array([loading_on_blade(b) for b in self.rotor.blades])

    def get_aerodynamic_state_derivatives(self, inputs, q_aero):
        # Calculate aerodynamic state derivatives
        wind_speed, rotor_speed, pitch = inputs
        factors = self._aerostates2factors(q_aero, wind_speed, rotor_speed)
        qd_aero = self.bem.inflow_derivatives(
            wind_speed, rotor_speed, pitch, factors)
        return qd_aero.flatten()

    def get_structural_state_derivatives(self, inputs, q_struct):
        # Calculate structural accelerations
        self.system.set_state(q_struct)
        self.system.solve_accelerations()
        zd = self.system.qd.dofs[:]
        zdd = self.system.qdd.dofs[:]
        return np.concatenate([zd, zdd])

    def get_state_derivatives(self, inputs, q_aero, q_struct):
        self.update_states(inputs, q_aero, q_struct)
        return np.concatenate([
            self.get_aerodynamic_state_derivatives(inputs, q_aero),
            self.get_structural_state_derivatives(inputs, q_struct),
        ])

    def do_aeroelasticity(self, wind_speed, rotor_speed, pitch,
                          q_aero, q_struct):
        # Apply aerodynamic loading to blades
        inputs = wind_speed, rotor_speed, pitch
        self.update_states(inputs, q_aero, q_struct)

        # Return aerodynamic state derivatives
        return self.get_aerodynamic_state_derivatives(inputs, q_aero)

    def find_equilibrium(self, wind_speed, rotor_speed, pitch):
        # Calculate initial aerodynamic states
        initial_factors = array(self.bem.solve(wind_speed, rotor_speed, pitch))
        q_aero = self._factors2aerostates(initial_factors, wind_speed,
                                          rotor_speed)

        # Set structural pitch
        for bearing in self.rotor.pitch_bearings:
            bearing.xstrain[:] = -pitch

        # Set blade loading with no velocities
        self.system.qd[:] = 0
        q_struct = self.system.get_state()
        self.do_aeroelasticity(wind_speed, rotor_speed, pitch, q_aero, q_struct)

        # Find equilibrium
        self.system.find_equilibrium()
        return self.system.q.dofs[:], q_aero

    def integrate(self, t1, dt, wind_speed_func, rotor_speed, pitch_angle,
                  print_progress=True):

        initial_dofs, initial_aero = self.find_equilibrium(
            wind_speed_func(0), rotor_speed, pitch_angle)
        assert all([bearing.xstrain[0] == -pitch_angle
                    for bearing in self.rotor.pitch_bearings])
        self.system.q.dofs[:] = initial_dofs
        self.system.qd['shaft-strains'][:] = rotor_speed
        self.system.update_kinematics()
        self.system.update_matrices()

        def callback(system, t, q_struct, q_aero):
            windspeed = wind_speed_func(t)
            qd_aero = self.do_aeroelasticity(windspeed, rotor_speed,
                                             pitch_angle, q_aero,
                                             q_struct)
            if self.dynamic_wake:
                return qd_aero
            else:
                return 0 * qd_aero

        integrator = mbwind.Integrator(self.system, outputs=('pos', 'vel'),
                                       method='dopri5')
        integrator.add_output(mbwind.LoadOutput('node-0', local=False))
        integrator.add_output(mbwind.LoadOutput('node-1', local=True))
        integrator.add_output(self.rotor.blades[0].output_deflections())
        integrator.add_output(mbwind.CustomOutput(
            lambda s: s.elements['blade1'].loading,
            label='blade loading'))
        integrator.integrate(t1, dt, callback=callback,
                             extra_states=initial_aero,
                             nprint=(10 if print_progress else None))

        if print_progress:
            print("\nResult contains the following outputs:")
            for i, label in enumerate(integrator.labels + ["aero states"]):
                print("[{:2}] {}".format(i, label))

        return integrator  # contains results

    def linearise_bem(self, windspeed, rotor_speed, pitch, perturbation=None):
        """
        Linearise BEM model about the operating point given by `windspeed`,
        `rotorspeed` and `pitch`.
        """
        if perturbation is None:
            perturbation = 1e-5  # could have a better default
        assert perturbation > 0

        # Find equilibrium operating point
        u0 = array([windspeed, rotor_speed, pitch])
        xs0, xa0 = self.find_equilibrium(windspeed, rotor_speed, pitch)
        xs0 = np.concatenate([xs0, 0*xs0])  # include velocities

        # Define output vector
        def get_outputs(u, xa, xs):
            self.update_states(u, xa, xs)
            self.system.solve_reactions()
            return np.concatenate([
                self.get_aerodynamic_loading(u, xa, xs).flatten(),
                -self.system.joint_reactions['node-0']
            ])
        y0 = get_outputs(u0, xa0, xs0)

        # Perturb
        Nx = len(xa0) + len(xs0)  # number of states
        Nu = len(u0)              # number of inputs

        def perturbA(delta, i):
            if i < len(xa0):
                xa = perturb_vector(xa0, i, delta)
                xs = xs0
            else:
                xa = xa0
                xs = perturb_vector(xs0, i - len(xa0), delta)
            return self.get_state_derivatives(u0, xa, xs)

        def perturbB(delta, i):
            u = perturb_vector(u0, i, delta)
            return self.get_state_derivatives(u, xa0, xs0)

        def perturbC(delta, i):
            if i < len(xa0):
                xa = perturb_vector(xa0, i, delta)
                xs = xs0
            else:
                xa = xa0
                xs = perturb_vector(xs0, i - len(xa0), delta)
            return get_outputs(u0, xa, xs)

        def perturbD(delta, i):
            u = perturb_vector(u0, i, delta)
            return get_outputs(u, xa0, xs0)

        h = perturbation
        A = array([derivative(perturbA, 0, h, args=(i,)) for i in range(Nx)]).T
        B = array([derivative(perturbB, 0, h, args=(i,)) for i in range(Nu)]).T
        C = array([derivative(perturbC, 0, h, args=(i,)) for i in range(Nx)]).T
        D = array([derivative(perturbD, 0, h, args=(i,)) for i in range(Nu)]).T
        return np.concatenate([xa0, xs0]), y0, (A, B, C, D)

    def linearise_structure(self, wind_speed, rotor_speed,
                            pitch_angle, azimuth, mbc=False,
                            perturbation=None):
        """Linearise structural model about the operating point given by
        `wind_speed`, `pitch_angle` and `azimuth`.
        """
        if perturbation is None:
            perturbation = 1e-5  # could have a better default
        assert perturbation > 0

        # Find equilibrium operating point
        xs0, xa0 = self.find_equilibrium(wind_speed, rotor_speed, pitch_angle)

        self.system.update_kinematics()
        z0 = {'shaft': [azimuth]}
        linsys = LinearisedSystem.from_system(self.system, z0,
                                              perturbation=perturbation)

        # Apply MBC transform if needed
        if mbc:
            iazimuth = self.system.free_dof_indices('shaft')[0]
            iblades = [self.system.free_dof_indices('blade{}'.format(i+1))
                       for i in range(3)]
            if mbc == 2:
                linsys = linsys.multiblade_transform2(iazimuth, iblades)
            else:
                linsys = linsys.multiblade_transform(iazimuth, iblades)

        return xs0, linsys
