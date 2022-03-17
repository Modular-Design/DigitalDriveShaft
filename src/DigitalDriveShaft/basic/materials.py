import numpy as np
from ansys.mapdl.core import Mapdl
from .failure import IFailure, IMAPDLFailure
from typing import Optional, List
from numpy import ndarray, array


class IMAPDLMaterial:
    def add_to_mapdl(self, mapdl: Mapdl, mat_id: int):
        raise NotImplementedError


class Material(IFailure, IMAPDLMaterial):
    def __init__(self, attr: dict, failure: Optional[IFailure] = None):
        self.attr = attr
        self.failure = failure

    def get_compliance(self) -> ndarray:
        raise NotImplementedError

    def get_stiffness(self) -> ndarray:
        return np.linalg.inv(self.get_compliance())

    def is_safe(self,
                stresses: Optional[List[float]] = None,
                strains: Optional[List[float]]  = None,
                temperature: Optional[List[float]] = None):
        if self.failure is not None:
            return self.failure.is_safe(stresses, strains, temperature)
        return True

    def add_to_mapdl(self, mapdl: Mapdl, mat_id: int):
        for (key, value) in self.attr.items():
            mapdl.mp(key, mat_id, value)
        if self.failure is not None:
            if isinstance(self.failure, IMAPDLFailure):
                self.failure.add_to_mapdl(mapdl, mat_id)


def get_plane_stress_stiffness(material):
    # get stiffness for plane stress
    elems = [0, 1, 5]  # ignore the s_zz, s_xy and s_yz row and column
    return material.get_stiffness()[elems][:, elems]


def get_plane_strain_stiffness(material):
    # get stiffness for plane stress
    elems = [0, 1, 5]  # ignore the s_zz, s_xy and s_yz row and column
    return np.linalg.inv(material.get_compliance()[elems][:, elems])


class OrthotropicMaterial(Material):
    def __init__(self,
                 E_x: float, E_y: float, E_z: float,
                 nu_xy: float, nu_xz: float, nu_yz: float,
                 G_xy: float, G_xz: float, G_yz: float,
                 density: float, **kwargs):
        self.E_x = E_x
        self.E_y = E_y
        self.E_z = E_z
        self.nu_xy = nu_xy
        self.nu_xz = nu_xz
        self.nu_yz = nu_yz
        self.G_xy = G_xy
        self.G_xz = G_xz
        self.G_yz = G_yz
        attr = dict(EX=E_x, EY=E_y, EZ=E_z,
                    PRXY=nu_xy, PRXZ=nu_xz, PRYZ=nu_yz,
                    GXY=G_xy, GXZ=G_xz, GYZ=G_yz,
                    DENS=density)
        super().__init__(attr, **kwargs)

    def get_compliance(self) -> ndarray:
        compliance = np.zeros((6,6))
        compliance[0, 0] = 1 / self.E_x
        compliance[1, 1] = 1 / self.E_y
        compliance[2, 2] = 1 / self.E_z
        compliance[3, 3] = 1 / self.G_yz
        compliance[4, 4] = 1 / self.G_zx
        compliance[5, 5] = 1 / self.G_xy

        compliance[1, 0] = compliance[0, 1] = - self.nu_xy / self.E_x
        compliance[2, 0] = compliance[0, 2] = - self.nu_xz / self.E_x
        compliance[2, 1] = compliance[1, 2] = - self.nu_yz / self.E_y

        return compliance


class IsotropicMaterial(Material):
    def __init__(self, Em: float, nu: float, density: float, **kwargs):
        attr = dict(EX=Em, PRXY=nu, DENS=density)
        self.Em = Em
        self.nu = nu
        super().__init__(attr, **kwargs)

    def get_compliance(self) -> ndarray:
        compliance = np.zeros((6,6))
        compliance[0, 0] = 1 / self.Em
        compliance[1, 1] = 1 / self.Em
        compliance[2, 2] = 1 / self.Em

        compliance[1, 0] = compliance[0, 1] = - self.nu / self.Em
        compliance[2, 0] = compliance[0, 2] = - self.nu / self.Em
        compliance[2, 1] = compliance[1, 2] = - self.nu / self.Em

        compliance[3, 3] = 2 * (1 + self.nu) / self.Em
        compliance[4, 4] = 2 * (1 + self.nu) / self.Em
        compliance[5, 5] = 2 * (1 + self.nu) / self.Em

        return compliance


class TransverselyIsotropicMaterial(OrthotropicMaterial):
    def __init__(self,
                 E_l: float, E_t: float,
                 nu_lt: float, nu_tt: float,
                 G_lt: float, G_tt: float, density: float, **kwargs):
        self.E_l = E_l
        self.E_t = E_t
        self.nu_lt = nu_lt
        self.nu_tt = nu_tt
        self.G_lt = G_lt
        super().__init__(E_x=E_l, E_y=E_t, E_z=E_t,
                         nu_xy=nu_lt, nu_xz=nu_lt, nu_yz=nu_tt,
                         G_xy=G_lt, G_xz=G_lt, G_yz=G_tt,
                         density=density)

    def get_compliance(self) -> ndarray:
        compliance = np.zeros((6,6))
        compliance[0, 0] = 1 / self.E_l
        compliance[1, 1] = 1 / self.E_t
        compliance[2, 2] = 1 / self.E_t

        compliance[1, 0] = compliance[0, 1] = - self.nu_lt / self.E_x
        compliance[2, 0] = compliance[0, 2] = - self.nu_lt / self.E_x
        compliance[2, 1] = compliance[1, 2] = - self.nu_tt / self.E_y

        compliance[3, 3] = (compliance[1, 1] - compliance[1, 2]) / 2
        compliance[4, 4] = 1 / self.G_lt
        compliance[5, 5] = 1 / self.G_lt

        return compliance
