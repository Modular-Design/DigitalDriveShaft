import math
from typing import Optional
from .coordfunc import CylindricalCoordFunction


class CylindricalForm(CylindricalCoordFunction):
    """
        A form best described in a cylindrical coordinate system.
    """
    def __init__(self,
                 r_func,
                 z_max: float, z_min: Optional[float] = 0,
                 phi_max: Optional[float] = 90, phi_min: Optional[float] = 0):
        super().__init__(r_func, z_max, z_min, phi_max, phi_min)

    def get_radius(self, z: float, phi=0.0) -> float:
        return super().get_value(z, phi)


class Cylinder(CylindricalForm):
    """
            A form with constant diameter an a certain length.
    """
    def __init__(self, diameter: float, length: float):
        def r_func(z, phi):
            return diameter/2.0
        super().__init__(r_func=r_func, z_max= length)