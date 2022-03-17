from ansys.mapdl.core import Mapdl
from typing import Optional, List
import numpy as np


class IFailure:
    def is_safe(self,
                stresses: Optional[List[float]] = None,
                strains: Optional[List[float]]  = None,
                temperature: Optional[List[float]] = None):
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


class OrthotropicMaxStressFailure(MAPDLFailure, IFailure):
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
