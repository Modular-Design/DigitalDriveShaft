from .orthotropicmaterial import OrthotropicMaterial, ndarray, np


class TransverselyIsotropicMaterial(OrthotropicMaterial):
    def __init__(self,
                 E_l: float, E_t: float,
                 nu_lt: float, nu_tt: float,
                 G_lt: float, G_tt: float, density: float,
                 **kwargs):
        self.E_l = E_l
        self.E_t = E_t
        self.nu_lt = nu_lt
        self.nu_tt = nu_tt
        self.G_lt = G_lt
        super().__init__(E_x=E_l, E_y=E_t, E_z=E_t,
                         nu_xy=nu_lt, nu_xz=nu_lt, nu_yz=nu_tt,
                         G_xy=G_lt, G_xz=G_lt, G_yz=G_tt,
                         density=density)

    def get_E1(self) -> float:
        return self.E_t

    def get_E2(self) -> float:
        return self.E_l

    def get_nu12(self) -> float:
        return self.nu_lt

    def get_nu21(self) -> float:
        return self.get_nu12() * self.get_E2() / self.get_E1()

    def get_compliance(self) -> ndarray:
        compliance = np.zeros((6, 6))
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