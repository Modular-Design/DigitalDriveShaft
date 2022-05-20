from .econtour import EContour
from .form import CylindricalForm, Cylinder
from .stackup import CylindricalStackup, Stackup
from typing import Optional, Union

import numpy as np


class DriveShaft:
    def __init__(self,
                 form: CylindricalForm,
                 stackup: CylindricalStackup,
                 contour: Optional[Union[EContour, float]] = EContour.INNER
                 ):
        self.form = form
        self.stackup = stackup
        self.contour = contour.value

        self.dz = 0.5
        self.dphi = 0
        self.phi_min = 0
        self.phi_max = 0

    def get_contour_factor(self) -> float:
        return self.contour

    def get_form(self) -> CylindricalForm:
        return self.form

    def get_stackup(self) -> CylindricalStackup:
        return self.stackup

    def get_value(self, z: float, phi: float, iso=True) -> (float, Stackup):  # z in [0,1], phi[0,1]
        return self.form.get_value(z, phi, iso), self.stackup.get_value(z, phi, iso)
    
    def get_inner_radius(self, z: float, phi: float, iso=True):
        radius, stackup = self.get_value(z, phi, iso)
        return radius + (0.0-self.get_contour_factor()) * stackup.get_thickness()

    def get_center_radius(self, z: float, phi: float, iso=True):
        radius, stackup = self.get_value(z, phi, iso)
        return radius + (0.5-self.get_contour_factor()) * stackup.get_thickness()

    def get_outer_radius(self, z: float, phi: float, iso=True):
        radius, stackup = self.get_value(z, phi, iso)
        return radius + (1.0-self.get_contour_factor()) * stackup.get_thickness()
    
    def get_length(self):
        return self.form.length()
    
    def get_cross_section(self, z: float, phi: float, iso=True):
        return np.pi/4.0 * (self.get_outer_radius(z, phi, iso) ** 2.0 - (self.get_inner_radius(z, phi, iso)) ** 2.0)  # Cross section of shaft


class SimpleDriveShaft(DriveShaft):
    def __init__(self,
                 diameter,
                 length,
                 stackup: Stackup,
                 contour: Optional[Union[EContour, float]] = EContour.INNER
                 ):
        def stackup_func(z, phi):
            return stackup
        cyl_stackup = CylindricalStackup(stackup_func)
        super().__init__(Cylinder(diameter, length), cyl_stackup, contour)

