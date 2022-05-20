from .ifalure import IFailure
from typing import Optional, List, Tuple, Union


class MaxStressFailure(IFailure):
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

        # this is only important when pyansys is installed!
        attr = dict(XTEN=self.strength[0][1], YTEN=self.strength[1][1], ZTEN=self.strength[2][1],
                    XCMP=self.strength[0][0], YCMP=self.strength[1][0], ZCMP=self.strength[2][0],
                    XY=self.strength[5][1], XZ=self.strength[4][1], YZ=self.strength[3][1],
                    XYCP=-1, XZCP=-1, YZCP=-1)

    def get_failure(self,
                    stresses: Optional[List[float]] = None,
                    strains: Optional[List[float]] = None,
                    temperature: Optional[float] = None):
        if stresses is None:
            raise ValueError("Need stress tensor in Voigt notation!")
        length = len(stresses)
        if length != 3 and length != 6:
            raise ValueError(f"Stresses has to be of length 3 (2d stress), but got length {length}")

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
