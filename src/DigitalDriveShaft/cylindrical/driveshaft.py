from ..basic import Stackup
from .econtour import EContour
from .form import CylindricalForm, Cylinder
from .stackup import CylindricalStackup

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

    def get_contour_factor(self) -> float:
        return self.contour

    def get_value_in_iso_scale(self, iso_z: float, iso_phi: float) -> (float, Stackup):  # z in [0,1], phi[0,1]
        return self.form.get_value_in_iso_scale(iso_z, iso_phi), self.stackup.get_value_in_iso_scale(iso_z, iso_phi)
    
    def get_inner_radius(self, iso_z: float, iso_phi: float):
        radius, stackup = self.get_value_in_iso_scale(iso_z, iso_phi)
        return radius + (0.0-self.get_contour_factor())*stackup.calc_thickness()

    def get_center_radius(self, iso_z: float, iso_phi: float):
        radius, stackup = self.get_value_in_iso_scale(iso_z, iso_phi)
        return radius + (0.5-self.get_contour_factor())*stackup.calc_thickness()
    
    def get_outer_radius(self, iso_z: float, iso_phi: float):
        radius, stackup = self.get_value_in_iso_scale(iso_z, iso_phi)
        return radius + (1.0-self.get_contour_factor())*stackup.calc_thickness()
    
    def get_length(self):
        return self.form.length()
    
    def get_Crosssection(self, iso_z: float, iso_phi: float):
        radius, stackup = self.get_value_in_iso_scale(iso_z, iso_phi)
        A_shaft = np.pi/4.0 * (self.get_outer_radius()**2.0 - (self.get_inner_radius())**2.0) #Cross section of shaft
        return A_shaft

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
