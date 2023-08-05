"""
Rotor model using mbwind
"""

import numpy as np
from numpy import pi, dot
from mbwind import RigidConnection, RigidBody, Hinge
from mbwind.utils import rotations, skewmat
from mbwind.elements.modal import ModalElementFromFE


def transform_rows(A, y):
    return np.einsum('ij,...aj->...ai', A, y)


class Rotor(object):
    def __init__(self, num_blades, root_length, blade_fe, num_modes=0,
                 damping=0, modes_spin=None, pitch=False):
        self.num_blades = num_blades
        self.root_length = root_length
        self.blade_fe = blade_fe

        # Build the elements
        self.roots = []
        self.blades = []
        self.pitch_bearings = []
        for ib in range(num_blades):
            R = rotations(('x', ib*2*pi/3), ('y', -pi/2))
            root_offset = dot(R, [root_length, 0, 0])
            root = RigidConnection('root%d' % (ib+1), root_offset, R)
            blade = ModalElementFromFE('blade%d' % (ib+1), blade_fe,
                                       num_modes, damping,
                                       reference_spin_speed=modes_spin)
            self.roots.append(root)
            self.blades.append(blade)

            if pitch:
                # Add bearing about blade X axis
                bearing = Hinge('pitch%d' % (ib+1), [1, 0, 0])
                self.pitch_bearings.append(bearing)
                root.add_leaf(bearing)
                bearing.add_leaf(blade)
            else:
                root.add_leaf(blade)

    @property
    def mass(self):
        return self.num_blades * self.blade_fe.mass

    def connect_to(self, parent):
        for root in self.roots:
            parent.add_leaf(root)

    def transform_blade_to_aero(self, y, pitch_angle=0):
        A = rotations(('z', -pitch_angle), ('y', -pi/2))
        return transform_rows(A, y)

    def transform_aero_to_blade(self, y, pitch_angle=0):
        A = rotations(('y', pi/2), ('z', pitch_angle))
        return transform_rows(A, y)

    def root_forces_from_aero_loading(self, loading):
        """loading is [out-of-plane, in-plane] force per unit length on blade.
        """
        r = self.blade_fe.q0[0::6]

        aero_loading = np.zeros(loading.shape[:-1] + (3,))
        aero_loading[..., 0:2] = loading

        F = np.trapz(aero_loading, r, axis=0)
        Q = np.trapz([dot(skewmat([0, 0, r[i]]), aero_loading[i, :])
                      for i in range(len(r))], r, axis=0)
        return np.r_[F, Q]

    def hub_forces_from_root_forces(self, forces):
        # Transform to hub loads (assuming all blades identical)
        hub = np.array([
            forces[0],
            0,
            0,
            forces[3] - self.root_length * forces[1],
            0,
            0,
        ])
        return self.num_blades * hub

    def hub_forces_from_aero_loading(self, loading):
        forces = self.root_forces_from_aero_loading(loading)
        return self.hub_forces_from_root_forces(forces)
