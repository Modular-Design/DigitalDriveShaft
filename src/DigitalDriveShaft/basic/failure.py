from ansys.mapdl.core import Mapdl #TODO: @Willi: Pfad funktioniert nicht
from typing import Optional, List, Tuple, Union
import numpy as np


class IFailure:
    def get_failure(self,
                stresses: Optional[List[float]] = None,
                strains: Optional[List[float]] = None,
                temperature: Optional[float] = None) -> dict:
        """
        Computes the loading dependent failure value.

        Parameters
        ----------
        stresses : List[float], optional
            stress tensor in Voigt notation

        strains : List[float], optional
            strain tensor using the Voigt notation:

        temperature: List[float, optional
            Temperature in [K]

        Notes
        -----
        - **stress** tensor in Voigt notation:

          + 2D: [sigma_11, sigma_22, sigma_12]
          + 3D: [sigma_11, sigma_22, sigma_33, sigma_23, sigma_13, sigma_12]

        - **strain** tensor using the Voigt notation:

          + 2D: [eps_11, eps_22, 2*eps_12]
          + 3D: [eps_11, eps_22, eps_33, 2*eps_23, 2*eps_13, 2*eps_12]

        Returns
        -------
        dict
            Dictionary of failure id and value.
            Values larger 1.0 a equivalent to a failure of the material.
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


class MaxStressFailure(MAPDLFailure, IFailure):
    def __init__(self,
                 stress_strength: List[Union[float, Tuple[float, float]]]):
        """
        Maximum-Stress Failure Criteria

        Parameters
        ----------
        stress_strength : List[Tuple[float, float]]
            strength tensor in Voigt notation

        Notes
        -----
        - strength tensor in Voigt notation with compression/min (comp) and tensile/max (tens) strength

          * 2D: [(comp_11, tens_11),
            (comp_22, tens_22),
            (comp_12, sigma_12)]
          * 3D: [(comp_11, tens_11),
            (comp_22, tens_22),
            (comp_33, tens_33),
            (comp_23, sigma_23),
            (comp_13, sigma_13),
            (comp_12, sigma_12)]

        - if **one** value is used instead of the tuple, then the is considerd the maximum value (so it should be positive)
          and the minimum will be assumed to be the negative version

        Examples
        --------
        Create a Plane-Maximum-Stress Failure Criteria

        >>> criteria = MaxStressFailure([(0.0, 2.0), (-2.0, 2.0), 2.0])
        >>> crit_loading = [4.0, 2.0, 0.0]
        >>> criteria.get_failure(stresses=crit_loading)
        returns {``max-stress``: 2.0}

        >>> uncrit_loading = [1.0, 1.0, 1.0]
        >>> criteria.get_failure(stresses=crit_loading)
        returns {``max-stress``: 0.5}
        """

        self.stress_mapping = [0, 1, 2, 3, 4, 5]
        length = len(stress_strength)
        if length == 3:
            self.stress_mapping = [0, 1, 1, 2, 2, 2]
        elif length != 3 or length != 6:
            raise ValueError(f"Stress-Strength Tensor has to be size 3 or 6! (Got: {length})")

        self.strength = []
        # generalize to s11, s22, s33, s23, s13, s12
        # note: sXY are tuples with (min, max)
        for i in range(6):
            strength = stress_strength[self.stress_mapping[i]]
            if not isinstance(strength, tuple):
                strength = (-strength, strength)
            self.strength.append(strength)

        attr = dict(XTEN=self.strength[0][1], YTEN=self.strength[1][1], ZTEN=self.strength[2][1],
                    XCMP=self.strength[0][0], YCMP=self.strength[1][0], ZCMP=self.strength[2][0],
                    XY=self.strength[5][1], XZ=self.strength[4][1], YZ=self.strength[3][1],
                    XYCP=-1, XZCP=-1, YZCP=-1)
        super().__init__(stress_attr=attr)

    def get_failure(self,
                stresses: Optional[List[float]] = None,
                strains: Optional[List[float]] = None,
                temperature: Optional[float] = None):
        if stresses is None:
            raise ValueError("Need stress tensor in Voigt notation!")
        length = len(stresses)
        if length != 3 or length != 6:
            raise ValueError("Stresses has to be of length 3 (2d stress)")

        load = []
        for i in range(6):
            load.append(stresses[self.stress_mapping[i]])

        factor = []
        for i in range(6):
            s_min, s_max = self.strength[i]
            middle = (s_max + s_min) / 2
            dist = (s_max - s_min) / 2
            factor.append(abs(load[i] - middle) / dist)
        return {"max_stress": max(factor)}


class CuntzeFailure(IFailure):
    def __init__(self,
                 E1: float,
                 R_1t: float, R_1c: float,
                 R_2t: float, R_2c:float, R_21: float,
                 my_21: Optional[float] = 0.3, interaction: Optional[float] = 2.5):
        """

        Parameters
        ----------
        E1
        R_1t
        R_1c
        R_2t
        R_2c
        R_21
        my_21
        interaction
        """
        # tes
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
                    temperature: Optional[float] = None):

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

