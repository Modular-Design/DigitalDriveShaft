import math
from typing import Optional


class CylindricalCoordFunction:
    """
        A function best described in a cylindrical coordinate system.
    """
    def __init__(self,
                 func,
                 z_max: float, z_min: Optional[float] = 0,
                 phi_max: Optional[float] = math.pi, phi_min: Optional[float] = -math.pi):
        self.func = func
        self.z_max = z_max
        self.z_min = z_min
        self.phi_min = phi_min
        self.phi_max = phi_max

    def get_value(self, z: float, phi=0.0):
        return self.func(z, phi)

    def get_value_in_iso_scale(self, iso_z: float, iso_phi: float): # z in [0,1], phi[0,1]
        z = iso_z * (self.max_z() - self.min_z()) + self.min_z()
        phi = iso_phi * (self.max_phi() - self.min_phi()) + self.min_phi()
        return self.get_value(z, phi)

    def min_z(self) -> float:
        return self.z_min

    def max_z(self) -> float:
        return self.z_max

    def min_phi(self) -> float:
        return self.phi_min

    def max_phi(self) -> float:
        return self.phi_max

    def length(self) -> float:
        return self.max_z() - self.min_z()

    def is_iso(self) -> bool:
        return self.min_z() == 0.0 and \
               self.max_z() == 1.0 and \
               self.min_phi() == 0.0 and \
               self.max_phi() == 1.0
