from ansys.mapdl.core import Mapdl
from typing import Optional, List
import numpy as np


class IFailure:
    def is_safe(self,
                stresses: Optional[List[float]] = None,
                strains: Optional[List[float]]  = None,
                temperature: Optional[List[float]] = None,
                Material):
        raise NotImplementedError
        
        #E1     E-Modulus in fibre direction
        #R_1t   tensile strength in fibre direction
        #R_1c   compressive strength in fibre direction
        #R_2t   tensile strength perpendicular to fibre direction
        #R_2c   compressive strength perpendicular to fibre direction
        #R_21   In-plane shear strength
        
        #epsilon_xt tensile strain in fibre direction
        #epsilon_xc compressive strain in fibre direction
        #sigma_yt   tensile stress perpendicular to fibre direction
        #sigma_yc   compressive stress perpendicular to fibre direction
        #sigma_y    stress perpendicular to fibre direction
        #tau_yx     in-plane shear stress
        
        
        my_21 = 0.3 #Reibungs-/Materialparameter 0 < My > 0.3
        m = 2.5     #Interaktionsfaktor 2,5 < m < 3,1
        
        #Reserve factors for single layer according to Cuntze
        RF_1sigma = Material.R_1t / (strains.epsilon_xt * Material.E1)    #FF1
        RF_1tau = Material.R_1c / (abs(strains.epsilon_xc) * Material.E1) #FF2
        
        RF_2sigma = Material.R_2t /stresses.sigma_yt             #IFF1
        RF_2tau = Material.R_2c / abs(stresses.sigma_yc)         #IFF2
        RF_21 = (Material.R_21 - my_21 * stresses.sigma_y) / abs(stresses.tau_yx)  #IFF2
        
        #total Reservefactor
        RF_ges = 1/((1/RF_1sigma)**m + (1/RF_1tau)**m + (1/RF_2sigma)**m + (1/RF_2tau)**m + (1/RF_21)**m)**(1/m)
        
        
        return RF_ges


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

    def is_safe(self,
                stresses: Optional[List[float]] = None,
                strains: Optional[List[float]] = None,
                temperature: Optional[List[float]] = None):
        if stresses is None:
            raise ValueError("stresses should be given")
        if len(stresses) != 3:  # TODO: should actually be 6 to be more general
            raise ValueError("stresses need to be in the format [sigma_ll, sigma_tt, tau_lt]")

        sl, st, tlt = stresses

        # Check if anything fails, value is True if it is outside the criteria.
        sl_tens = np.any(sl >= self.sl_max)
        sl_comp = np.any(-self.sl_min >= sl)
        st_tens = np.any(st >= self.st_max)
        st_comp = np.any(-self.st_min >= st)
        shear = np.any(np.abs(tlt) >= self.tlt)  # ignore ttt
        if any([sl_tens, sl_comp, st_tens, st_comp, shear]):
            return False
        return True
