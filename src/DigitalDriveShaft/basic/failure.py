from ansys.mapdl.core import Mapdl
from typing import Optional, List
import numpy as np


class IFailure:
    def get_failure(self,
                stresses: Optional[List[float]] = None,
                strains: Optional[List[float]] = None,
                temperature: Optional[List[float]] = None) -> dict:
        """
            kapazität: 100, Beanspruchung: 70 -> 100 / 70
            belastung / kapazität -> f < 1.0 -> sicher, f > 1.0 unsicher
            Anstrengung
            f < 1/1.5
        Args:
            stresses:
            strains:
            temperature:

        Returns:
            {"failure_id": }
        """
        raise NotImplementedError


class IMAPDLFailure:
    def add_to_mapdl(self, mapdl: Mapdl, mat_id: int):
        raise NotImplementedError


class MAPDLFailure(IMAPDLFailure):
    def __init__(self,
                 stress_attr: Optional[dict] = None,
                 strain_attr: Optional[dict] = None,
                 temperature_attr: Optional[dict] = None,
                 ):
        if stress_attr is None:
            stress_attr = dict()
        self.stress_attr = stress_attr

        if strain_attr is None:
            strain_attr = dict()
        self.strain_attr = strain_attr

        if temperature_attr is None:
            temperature_attr = dict()
        self.temperature_attr = temperature_attr

    def add_to_mapdl(self, mapdl: Mapdl, mat_id: int):
        for (key, value) in self.stress_attr.items():
            mapdl.fc(mat_id,  "S", key, value)

        for (key, value) in self.strain_attr.items():
            mapdl.fc(mat_id,  "TEMP", key, value)

        for (key, value) in self.temperature_attr.items():
            mapdl.fc(mat_id,  "EPEL", key, value)


class PlaneMaxStressFailure(MAPDLFailure, IFailure):
    def __init__(self,
                 tens_l: float, tens_t: float,
                 shear_lt: float, shear_tt: float,
                 compr_l: float, compr_t: float):
        self.sl_max = tens_l
        self.st_max = tens_t
        self.sl_min = compr_l
        self.st_min = compr_t
        self.tlt = shear_lt
        self.ttt = shear_tt

        attr = dict(XTEN=tens_l, YTEN=tens_t, ZTEN=tens_t,
                    XCMP=compr_l, YCMP=compr_t, ZCMP=compr_t,
                    XY=shear_lt, XZ=shear_lt, YZ=shear_tt,
                    XYCP=-1, XZCP=-1, YZCP=-1)
        super().__init__(stress_attr=attr)

    def get_failure(self,
                stresses: Optional[List[float]] = None,
                strains: Optional[List[float]] = None,
                temperature: Optional[List[float]] = None):
        if stresses is None:
            raise ValueError("stresses should be given")
        if len(stresses) != 3:  # TODO: should actually be 6 to be more general
            raise ValueError("stresses need to be in the format [sigma_ll, sigma_tt, tau_lt]")

        sl, st, tlt = stresses

        sl_middle = (self.sl_max + self.sl_min) / 2
        sl_dist = (self.sl_max - self.sl_min) / 2
        sl_factor = abs(sl - sl_middle) / sl_dist

        st_middle = (self.st_max + self.st_min) / 2
        st_dist = (self.st_max - self.st_min) / 2
        st_factor = abs(st - st_middle) / st_dist
        shear_factor = np.abs(tlt) / self.tlt  # ignore ttt
        return {"max_stress": max(sl_factor, st_factor, shear_factor)}


class CuntzeFailure(IFailure):
    def __init__(self,
                 E1: float,
                 R_1t: float, R_1c: float,
                 R_2t: float, R_2c:float, R_21: float,
                 my_21: Optional[float] = 0.3, interaction: Optional[float] = 2.5):
        """

        Args:
            E1: E-Modulus in fibre direction
            R_1t: tensile strength in fibre direction
            R_1c: compressive strength in fibre direction
            R_2t: tensile strength perpendicular to fibre direction
            R_2c: compressive strength perpendicular to fibre direction
            R_21: In-plane shear strength
            my_21: Reibungs-/Materialparameter 0 < My > 0.3
            interaction:  Interaktionsfaktor 2,5 < m < 3,1
        """

        self.E1 = E1
        self.R_1t = R_1t
        self.R_1c = R_1c
        self.R_2t = R_2t
        self.R_2c = R_2c
        self.R_21 = R_21
        self.my_21 = my_21
        self.interaction = interaction
        pass

    def get_failure(self,
                    stresses: Optional[List[float]] = None,
                    strains: Optional[List[float]] = None,
                    temperature: Optional[List[float]] = None):

        # epsilon_xt tensile strain in fibre direction
        # epsilon_xc compressive strain in fibre direction
        # sigma_yt   tensile stress perpendicular to fibre direction
        # sigma_yc   compressive stress perpendicular to fibre direction
        # sigma_y    stress perpendicular to fibre direction
        # tau_yx     in-plane shear stress
        my_21 = 0.3  # Reibungs-/Materialparameter 0 < My > 0.3
        m = self.interaction  # Interaktionsfaktor 2,5 < m < 3,1

        # Reserve factors for single layer according to Cuntze

        epsilon_x = strains[0]
        epsilon_xt = 0.0
        epsilon_xc = 0.0
        if epsilon_x > 0:
            epsilon_xt = epsilon_x
        else:
            epsilon_xc = epsilon_x

        sigma_y = stresses[1]
        sigma_yt = 0.0
        sigma_yc = 0.0
        if sigma_y > 0:
            sigma_yt = sigma_y
        else:
            sigma_yc = sigma_y

        tau_yx = stresses[2]

        RF_1sigma = self.R_1t / (epsilon_xt * self.E1)  # FF1
        RF_1tau = self.R_1c / (abs(epsilon_xc) * self.E1)  # FF2

        RF_2sigma = self.R_2t / sigma_yt  # IFF1
        RF_2tau = self.R_2c / abs(sigma_yc)  # IFF2
        RF_21 = (self.R_21 - self.my_21 * sigma_y) / abs(tau_yx)  # IFF2

        # total Reservefactor
        RF_ges = 1 / ((1 / RF_1sigma) ** m + (1 / RF_1tau) ** m + (1 / RF_2sigma) ** m + (1 / RF_2tau) ** m + (
                    1 / RF_21) ** m) ** (1 / m)

        return {"cuntze": RF_ges}

