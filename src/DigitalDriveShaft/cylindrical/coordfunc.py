from typing import Optional


class CylindricalCoordFunction:
    """
    A function best described in a cylindrical coordinate system.
    """

    def __init__(self, func, z_max: float, z_min: Optional[float] = 0):
        self.func = func
        self.z_max = z_max
        self.z_min = z_min

    def get_value(self, z: float, phi: float, iso=True):
        """
        if iso:
            z in [0,1]
            phi in [-pi, pi]
        else:
            no restrictions
        Returns:
            radius
        """
        if iso:
            z = z * (self.max_z() - self.min_z()) + self.min_z()
        return self.func(z, phi)

    def min_z(self) -> float:
        return self.z_min

    def max_z(self) -> float:
        return self.z_max

    def length(self) -> float:
        return self.max_z() - self.min_z()

    def is_iso(self) -> bool:
        return self.min_z() == 0.0 and self.max_z() == 1.0
