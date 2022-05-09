from .ifalure import IFailure
from typing import Optional, List


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

        References
        ---------
        .. [1] R.G. Cuntze and A. Freund, "The predictive capability of failure mode concept-based strength criteria
           for multidirectional laminates", Composites Science and Technology, vol. 64, no. 3, pp. 343-377, 2004

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
