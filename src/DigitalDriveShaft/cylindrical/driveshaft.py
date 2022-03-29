import numpy as np

from ..basic import Stackup, Mapdl, IMAPDL
from ..sim.elements import Shell181, Solid185
from .econtour import EContour
from .form import CylindricalForm, Cylinder
from .stackup import CylindricalStackup


from typing import Optional, Union

import numpy as np


class DriveShaft(IMAPDL):
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
    
    def get_Crosssection(self, z: float, phi: float, iso=True):
        return np.pi/4.0 * (self.get_outer_radius(z, phi, iso) ** 2.0 - (self.get_inner_radius(z, phi, iso)) ** 2.0)  # Cross section of shaft

    def add_to_mapdl(self, mapdl: Mapdl, **kwargs):
        mapdl.csys(1)

        self.dz = kwargs.get("dz")
        if self.dz is None:
            self.dz = 5 / 8.

        self.dphi = kwargs.get("dphi")
        if self.dphi is None:
            self.dphi = np.pi / 16

        self.phi_min = kwargs.get("phi_min")
        if self.phi_min is None:
            self.phi_min = 0

        self.phi_max = kwargs.get("phi_max")
        if self.phi_max is None:
            self.phi_max = np.pi/2

        element_type = kwargs.get("type")
        if element_type is None:
            element_type = "SHELL"

        if element_type == "SHELL":
            self.__mesh_with_shell__(mapdl)
        elif element_type == "SOLID":
            self.__mesh_with_shell__(mapdl)

    def __mesh_with_shell__(self, mapdl: Mapdl):
        start_id = 1
        zs = np.arange(self.form.min_z(), self.form.max_z() + self.dz, self.dz)
        phis = np.arange(self.phi_min, self.phi_max + self.dphi, self.dphi)
        k_start = start_id
        k_id = k_start
        for phi in phis:
            for z in zs:
                r = self.get_center_radius(z, phi, False)
                mapdl.k(k_id, r, phi / np.pi * 180, z)
                k_id += 1
        k_end = k_id - 1
        # mapdl.kplot()

        z_divs = len(zs) - 1
        phi_divs = len(phis) - 1
        combinations = z_divs * phi_divs
        rel_positions = [0] * combinations
        # areas first in z-direction then in phi
        index = 0
        for i in range(phi_divs):
            for j in range(z_divs):
                # counter clockwise
                rel_positions[index] = ((j + (j+1)) / (2 * len(zs)), (phis[i] + phis[i+1]) / 2)
                index += 1
                """
                d - c
                |   |
                a - b
                """
                a = i * (z_divs + 1) + j + 1
                b = (i + 1) * (z_divs + 1) + j + 1
                c = (i + 1) * (z_divs + 1) + j + 2
                d = i * (z_divs + 1) + j + 2
                mapdl.a(a, b, c, d)

        element = Shell181(1)
        element.set_integration(2)
        element.set_layer_storage(1)
        element.add_to_mapdl(mapdl)
        for i in range(combinations):
            z, phi = rel_positions[i]
            laminat = self.stackup.get_value(z, phi)
            plies = laminat.get_plies()
            id = i+1
            mapdl.sectype(secid=id, type_="SHELL", name="shell181")
            for ply in plies:
                material = ply.get_material()
                mat_id = material.get_id()
                if mat_id == 0:
                    raise ValueError(f"No material id given for ply {i}")
                mapdl.secdata(ply.get_thickness(), mat_id, ply.get_rotation(), 5)
            mapdl.asel("S", "AREA", '', i+1)
            mapdl.esize(0, 1)
            mapdl.type(1)
            mapdl.secnum(id)
            mapdl.amesh("ALL")

    def __mesh_with_solid__(self, mapdl: Mapdl):
        dz = 1.0
        dphi = 45.0
        start_id = 1
        zs = np.arange(self.form.min_z(), self.form.max_z() + self.dz, self.dz)
        phis = np.arange(0, self.form.max_phi() + self.dphi, self.dphi)
        k_start = start_id
        k_id = k_start

        for i in range(len(phis)):
            for j in range(len(zs)):

                r = self.form.get_value(zs[j], phis[i])
                mapdl.k(k_id, r, phis[i], zs[j])
                k_id += 1
        k_end = k_id - 1

        dots_in_z_direction = len(zs)
        combinations = (len(phis) - 1) * (len(zs) - 1)
        rel_positions = [0] * combinations





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

