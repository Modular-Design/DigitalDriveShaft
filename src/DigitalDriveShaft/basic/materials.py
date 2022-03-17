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

    def get_stiffness(self) -> ndarray:
        raise NotImplementedError

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


class AnisotropicMaterial(Material):
    def __init__(self,
                 E_x:float, E_y: float, E_z: float,
                 nu_xy: float, nu_xz: float, nu_yz: float,
                 G_xy: float, G_xz: float, G_yz: float,
                 density: float, **kwargs):
        attr = dict(EX=E_x, EY=E_y, EZ=E_z,
                    PRXY=nu_xy, PRXZ=nu_xz, PRYZ=nu_yz,
                    GXY=G_xy, GXZ=G_xz, GYZ=G_yz,
                    DENS=density)
        super().__init__(attr, **kwargs)


class IsotropicMaterial(Material):
    def __init__(self, Em: float, nu: float, density: float, **kwargs):
        attr = dict(EX=Em, PRXY=nu, DENS=density)
        super().__init__(attr, **kwargs)


class OrthotropicMaterial(AnisotropicMaterial):
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

    def get_stiffness(self) -> ndarray:
        # TODO: actually describes planar stress
        nu_tl = self.nu_lt * self.E_t / self.E_l
        return array([[self.E_l/(1 - self.nu_lt*nu_tl), (self.nu_lt*self.E_t)/(1 - self.nu_lt * nu_tl), 0],
                     [(nu_tl * self.E_l)/(1 - self.nu_lt*nu_tl), self.E_t/(1 - self.nu_lt * nu_tl), 0],
                     [0, 0, self.G_lt]])
