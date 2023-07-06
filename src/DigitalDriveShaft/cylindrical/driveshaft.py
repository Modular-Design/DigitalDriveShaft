from .econtour import EContour
from .form import CylindricalForm, Cylinder
from .stackup import CylindricalStackup, Stackup
from typing import Optional, Union

import numpy as np


class DriveShaft:
    def __init__(
        self,
        form: CylindricalForm,
        stackup: CylindricalStackup,
        contour: Optional[Union[EContour, float]] = EContour.INNER,
    ):
        self.form = form
        self.stackup = stackup

        if isinstance(contour, EContour):
            contour = contour.value
        self.contour = contour

        self.n_z = 100
        self.n_phi = 10

        self.volume = None
        self.mass = None
        self.calc_volume()
        self.calc_mass()

    def get_contour_factor(self) -> float:
        return self.contour

    def get_form(self) -> CylindricalForm:
        return self.form

    def get_stackup(self) -> CylindricalStackup:
        return self.stackup

    def get_value(
        self, z: float, phi: float, iso=True
    ) -> (float, Stackup):  # z in [0,1], phi[0,1]
        return self.form.get_value(z, phi, iso), self.stackup.get_value(z, phi, iso)

    def get_radius(
        self,
        z: float,
        phi: float,
        contour: Optional[Union[EContour, float]],
        iso: Optional[bool] = True,
    ):
        radius, stackup = self.get_value(z, phi, iso)
        thickness = stackup.get_thickness()
        if isinstance(contour, EContour):
            contour = contour.value
        return radius + (contour - self.get_contour_factor()) * thickness

    def get_inner_radius(self, z: float, phi: float, iso=True):
        radius, stackup = self.get_value(z, phi, iso)
        return radius + (0.0 - self.get_contour_factor()) * stackup.get_thickness()

    def get_center_radius(self, z: float, phi: float, iso=True):
        radius, stackup = self.get_value(z, phi, iso)
        return radius + (0.5 - self.get_contour_factor()) * stackup.get_thickness()

    def get_outer_radius(self, z: float, phi: float, iso=True):
        radius, stackup = self.get_value(z, phi, iso)
        return radius + (1.0 - self.get_contour_factor()) * stackup.get_thickness()

    def get_length(self):
        return self.form.length()

    def get_cross_section(self, z: float, iso=True):
        area = 0.0
        dphi = 2.0 * np.pi / self.n_phi
        for phi in np.arange(-np.pi, np.pi, dphi):
            radius, stackup = self.get_value(z, phi, iso)
            radius = (
                radius + (0.5 - self.get_contour_factor()) * stackup.get_thickness()
            )
            area += radius * stackup.get_thickness()
        area *= dphi
        return area

    def get_area_mass(self, z: float, iso=True):
        area_mass = 0.0
        dphi = 2.0 * np.pi / self.n_phi
        for phi in np.arange(-np.pi, np.pi, dphi):
            radius, stackup = self.get_value(z, phi, iso)
            radius = radius + (self.get_contour_factor()) * stackup.get_thickness()
            line_mass = 0.0
            plies = stackup.get_plies()
            for ply in plies:
                thickness = ply.get_thickness()
                density = ply.get_material().get_density()
                line_mass += (radius + 0.5 * thickness) * density * thickness
                radius += thickness
            area_mass += line_mass
        area_mass *= dphi
        return area_mass

    def calc_volume(self):
        # \int_v r dr d\phi dz
        vol = 0.0
        dz = 1.0 / self.n_z
        for z in np.arange(dz, 1, dz):
            vol += self.get_cross_section(z)
        vol += 0.5 * (self.get_cross_section(0) + self.get_cross_section(1))
        vol *= dz * self.form.length()
        self.volume = vol
        return vol

    def get_volume(self):
        return self.volume

    def calc_mass(self):
        mass = 0.0
        dz = 1.0 / self.n_z
        for z in np.arange(dz, 1, dz):
            mass += self.get_area_mass(z)
        mass += 0.5 * (self.get_area_mass(0) + self.get_area_mass(1))
        mass *= dz * self.form.length()
        self.mass = mass
        return mass

    def get_mass(self):
        return self.mass

    def calc_density(self):
        self.calc_volume()
        self.calc_mass()

        return self.get_density()

    def get_density(self):
        return self.mass / self.volume


class SimpleDriveShaft(DriveShaft):
    def __init__(
        self,
        diameter,
        length,
        stackup: Stackup,
        contour: Optional[Union[EContour, float]] = EContour.INNER,
    ):
        def stackup_func(z, phi):
            return stackup

        cyl_stackup = CylindricalStackup(stackup_func)
        super().__init__(Cylinder(diameter, length), cyl_stackup, contour)

    def get_cross_section(self, z: float, iso=True):
        """returns the crossection of a circle

        Parameters
        ----------
        z
        iso

        Returns
        -------

        """
        return (
            np.pi
            / 4.0
            * (
                self.get_outer_radius(z, 0.0, iso) ** 2.0
                - (self.get_inner_radius(z, 0.0, iso)) ** 2.0
            )
        )
