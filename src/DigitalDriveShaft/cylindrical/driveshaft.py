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
            self.__mesh_with_solid__(mapdl)

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
                mapdl.secdata(ply.get_thickness(), mat_id, ply.get_rotation() * 180 / np.pi + 90, 5)
            mapdl.asel("S", "AREA", '', i+1)
            mapdl.esize(0, 1)
            mapdl.type(1)
            mapdl.secnum(id)
            mapdl.amesh("ALL")

    def __mesh_with_solid__(self, mapdl: Mapdl):
        start_id = 1
        zs = np.arange(self.form.min_z(), self.form.max_z() + self.dz, self.dz)
        phis = np.arange(self.phi_min, self.phi_max + self.dphi, self.dphi)
        k_start = start_id
        k_id = k_start

        n_plies = len(self.stackup.get_value(0, 0).get_plies())

        for phi in phis:
            for z in zs:
                laminat = self.stackup.get_value(z, phi, iso=False)
                plies = laminat.get_plies()

                r = self.get_inner_radius(z, phi, iso=False)
                mapdl.k(k_id, r, phi / np.pi * 180, z)
                k_id += 1
                for ply in plies:
                    r += ply.get_thickness()
                    mapdl.k(k_id, r, phi / np.pi * 180, z)
                    k_id += 1
        k_end = k_id - 1
        # mapdl.kplot(show_bounds=True, show_keypoint_numbering=True)

        n_phis = len(phis)
        n_zs = len(zs)
        z_offset = n_plies + 1
        phi_offset = n_zs * z_offset
        v_id = 1
        mapdl.et(1, "SOLID186")
        # mapdl.smrtsize("OFF")
        for j in range(n_phis - 1):
            for i in range(n_zs - 1):
                """
                d - c
                |   |
                a - b
                """
                a = j * phi_offset + i * z_offset
                b = (j + 1) * phi_offset + i * z_offset
                c = (j + 1) * phi_offset + (i + 1) * z_offset
                d = j * phi_offset + (i + 1) * z_offset

                z_mid = (zs[i] + zs[i + 1]) / 2.0
                phi_mid = (phis[j] + phis[j + 1]) / 2.0
                laminat = self.stackup.get_value(z_mid, phi_mid, False)
                plies = laminat.get_plies()

                self.stackup.get_value(0, 0).get_plies()
                for p in range(n_plies):
                    """
                    top:
                    p8 - p7
                    |    |
                    p5 - p6
                    
                    bottom 
                    p4 - p3
                    |    |
                    p1 - p2
                    """
                    p1 = a + p + 1
                    p2 = b + p + 1
                    p3 = c + p + 1
                    p4 = d + p + 1

                    p5 = a + p + 2
                    p6 = b + p + 2
                    p7 = c + p + 2
                    p8 = d + p + 2
                    mapdl.v(p1, p2, p3, p4, p5, p6, p7, p8)
                    # if v_id > 10:
                    #     print(v_id)
                    #     mapdl.vsel("S", "VOLU", '', "ALL")
                    #     mapdl.vplot()
                    mapdl.vsel("S", "VOLU", '', v_id)
                    mapdl.esize(0, 1)
                    mapdl.mat(plies[p].get_material().get_id())
                    mapdl.vmesh("ALL")
                    mapdl.local(v_id, 1, 0, 0, 0, plies[p].get_rotation() / np.pi * 180.0 + 90)
                    mapdl.esel("S", "ELEM", "", v_id)
                    mapdl.emodif("all", "ESYS", v_id)
                    v_id += 1

        k_end = k_id - 1
        mapdl.vsel("S", "VOLU", '', "ALL")
        mapdl.esel("S", "ELEM", "", "ALL")



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

