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

    def get_contour_factor(self) -> float:
        return self.contour

    def get_form(self) -> CylindricalForm:
        return self.form

    def get_stackup(self) -> CylindricalStackup:
        return self.stackup

    def get_value_in_iso_scale(self, iso_z: float, iso_phi: float) -> (float, Stackup):  # z in [0,1], phi[0,1]
        return self.form.get_value_in_iso_scale(iso_z, iso_phi), self.stackup.get_value_in_iso_scale(iso_z, iso_phi)
    
    def get_inner_radius(self, iso_z: float, iso_phi: float):
        radius, stackup = self.get_value_in_iso_scale(iso_z, iso_phi)
        return radius + (0.0-self.get_contour_factor())*stackup.get_thickness()

    def get_center_radius(self, iso_z: float, iso_phi: float):
        radius, stackup = self.get_value_in_iso_scale(iso_z, iso_phi)
        return radius + (0.5-self.get_contour_factor())*stackup.get_thickness()
    
    def get_outer_radius(self, iso_z: float, iso_phi: float):
        radius, stackup = self.get_value_in_iso_scale(iso_z, iso_phi)
        return radius + (1.0-self.get_contour_factor())*stackup.get_thickness()
    
    def get_length(self):
        return self.form.length()
    
    def get_Crosssection(self, iso_z: float, iso_phi: float):
        radius, stackup = self.get_value_in_iso_scale(iso_z, iso_phi)
        A_shaft = np.pi/4.0 * (self.get_outer_radius()**2.0 - (self.get_inner_radius())**2.0)  # Cross section of shaft
        return A_shaft

    def add_to_mapdl(self, mapdl: Mapdl, **kwargs):
        mapdl.csys(1)
        element_type = kwargs.get("type")
        if element_type is None:
            element_type = "SHELL"

        if element_type == "SHELL":
            self.__mesh_with_shell__(mapdl)
        elif element_type == "SOLID":
            self.__mesh_with_shell__(mapdl)

    def __mesh_with_shell__(self, mapdl: Mapdl):
        dz = 5  # 0.1
        dphi = np.pi / 16  # 4
        start_id = 1
        zs = np.arange(self.form.min_z(), self.form.max_z() + dz, dz)
        phis = np.arange(-np.pi, np.pi + dphi, dphi)
        k_start = start_id
        k_id = k_start
        for i in range(len(phis)):
            for j in range(len(zs)):
                r = self.form.get_value(zs[j], phis[i])
                mapdl.k(k_id, r, phis[i] / np.pi * 180, zs[j])
                k_id += 1
        k_end = k_id - 1
        # mapdl.kplot()

        dots_in_z_direction = len(zs)
        combinations = (len(phis) - 1) * (len(zs) - 1)
        rel_positions = [0] * combinations
        # areas first in z-direction then in phi
        for i in range(len(phis) - 1):
            for j in range(len(zs)-1):
                pos = i * dots_in_z_direction + k_start
                pos_left = (i + 1) * dots_in_z_direction + k_start
                # counter clockwise
                index = i * (len(zs)-1) + k_start + j - 1
                rel_positions[index] = ((j + (j+1)) / (2 * len(zs)), (i + (i+1)) / (2 * len(phis)))
                """
                d - c
                |   |
                a - b
                """
                a = pos + j
                b = pos_left + j
                c = pos_left + j + 1
                d = pos + j + 1
                mapdl.a(a, b, c, d)
                # mapdl.aplot(show_area_numbering=True, show_bounds=True)

        for i in range(combinations):
            z, phi = rel_positions[i]
            laminat = self.stackup.get_value_in_iso_scale(z, phi)
            element = Shell181(i+1)
            element.set_layer_storage(1)
            plies = laminat.get_plies()
            for p in range(len(plies)):
                ply = plies[p]
                material = ply.get_material()
                mat_id = material.get_id()
                if mat_id == 0:
                    raise ValueError(f"No material id given for ply {i}")
                # material.add_to_mapdl(mapdl)
                element.add_layer(ply.get_thickness(), mat_id, ply.get_rotation(), 3)
            element.add_to_mapdl(mapdl)
            mapdl.secoffset("BOT")
            mapdl.asel("S", "AREA", '', i+1)
            mapdl.esize(0, 1)
            mapdl.type(i+1)
            mapdl.amesh("ALL")
            # mapdl.eplot(show_node_numbering=True)

    def __mesh_with_solid__(self, mapdl: Mapdl):
        dz = 1.0
        dphi = 45.0
        start_id = 1
        zs = np.arange(self.form.min_z(), self.form.max_z() + dz, dz)
        phis = np.arange(self.form.min_phi(), self.form.max_phi() + dphi, dphi)
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

