from ansys.mapdl.core import Mapdl


class Material:
    def __init__(self, attr: dict):
        self.attr = attr

    def add_to_mapdl(self, mapdl: Mapdl, mat_id: int):
        for (key, value) in self.attr.items():
            mapdl.mp(key, mat_id, value)


class AnisotropicMaterial(Material):
    def __init__(self,
                 E_x:float, E_y: float, E_z: float,
                 nu_xy: float, nu_xz: float, nu_yz: float,
                 G_xy: float, G_xz: float, G_yz: float,
                 density: float):
        attr = dict(EX=E_x, EY=E_y, EZ=E_z,
                    PRXY=nu_xy, PRXZ=nu_xz, PRYZ=nu_yz,
                    GXY= G_xy, GXZ=G_xz, GYZ=G_yz,
                    DENS=density)
        super().__init__(attr)


class IsotropicMaterial(Material):
    def __init__(self, Em: float, nu: float, density: float):
        attr = dict(EX=Em, PRXY=nu, DENS=density)
        super().__init__(attr)


class OrthotropicMaterial(AnisotropicMaterial):
    def __init__(self,
                 E_l: float, E_t: float,
                 nu_lt: float, nu_tt: float,
                 G_lt: float, G_tt: float, density: float):
        super().__init__(E_x=E_l, E_y=E_t, E_z=E_t,
                         nu_xy=nu_lt, nu_xz=nu_lt, nu_yz=nu_tt,
                         G_xy=G_lt, G_xz=G_lt, G_yz=G_tt,
                         density=density)

