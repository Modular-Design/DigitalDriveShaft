import math
from .stackup import Stackup
from .econtour import EContour
from typing import Optional, Union


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


class CylindricalForm(CylindricalCoordFunction):
    """
        A form best described in a cylindrical coordinate system.
    """
    def __init__(self,
                 r_func,
                 z_max: float, z_min: Optional[float] = 0,
                 phi_max: Optional[float] = math.pi, phi_min: Optional[float] = -math.pi):
        super().__init__(r_func, z_max, z_min, phi_max, phi_min)

    def get_radius(self, z: float, phi=0.0) -> float:
        return super().get_value(z, phi)


class Cylinder(CylindricalForm):
    """
            A form with constant diameter an a certain length.
    """
    def __init__(self, diameter: float, length: float):
        def r_func(z, phi):
            return diameter/2.
        super().__init__(r_func=r_func, z_max=length)


class CylindricalStackup(CylindricalCoordFunction):
    """
            A stackup best described in a cylindrical coordinate system.
    """
    def __init__(self,
                 laminat_func,
                 z_max: float, z_min: Optional[float] = 0,
                 phi_max: Optional[float] = math.pi, phi_min: Optional[float] = -math.pi):
        super().__init__(laminat_func, z_max, z_min, phi_max, phi_min)

    def get_laminat(self, z: float, phi: float) -> Stackup:  # laminat is not dependent on r:
        return super().get_value(z, phi)


class DriveShaft:
    def __init__(self,
                 form: CylindricalForm,
                 stackup: CylindricalStackup,
                 contour: Optional[Union[EContour, float]] = EContour.INNER
                 ):
        self.form = form
        self.stackup = stackup
        self.contour = contour.value

    def get_contour_factor(self) -> float:
        return self.contour

    def get_value_in_iso_scale(self, iso_z: float, iso_phi: float) -> (float, Stackup):  # z in [0,1], phi[0,1]
        return self.form.get_value_in_iso_scale(iso_z, iso_phi), self.stackup.get_value_in_iso_scale(iso_z, iso_phi)


class SimpleDriveShaft(DriveShaft):
    def __init__(self,
                 diameter,
                 length,
                 stackup: Stackup,
                 contour: Optional[Union[EContour, float]] = EContour.INNER
                 ):
        def stackup_func(z, phi):
            return stackup
        cyl_stackup = CylindricalStackup(stackup_func, 1.0, 0.0, 1.0, 0.0)
        super().__init__(Cylinder(diameter, length), cyl_stackup, contour)
