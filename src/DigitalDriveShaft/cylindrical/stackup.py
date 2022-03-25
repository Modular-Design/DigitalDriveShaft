import math
from typing import Optional
from ..basic import Stackup
from .coordfunc import CylindricalCoordFunction


class CylindricalStackup(CylindricalCoordFunction):
    """
            A stackup best described in a cylindrical coordinate system.
    """
    def __init__(self,
                 laminat_func,
                 z_max: Optional[float] = 1, z_min: Optional[float] = 0):
        super().__init__(laminat_func, z_max, z_min)

    def get_laminat(self, z: float, phi: float) -> Stackup:  # laminat is not dependent on r:
        return super().get_value(z, phi)
