import numpy as np


# Voigt limit of the rule of mixtures.
def voigt(C1, C2, volf):
    """
    Calculate the mixed stiffness matrix with the Voigt.
    This upper limit of the rule of mixtures is generaly used for the
    longitudional stiffness :math:`E_l`.
    Parameters
    ----------
    C1 : matrix
        The stiffness matrix of material 1.
    C2 : float
        The stiffness matrix of material 2.
    volf : matrix
        The volume fraction of material 1.
    Returns
    -------
    C_hat : matrix
        The stiffness matrix of the mixed material.
    S_hat : matrix
        The compliance matrix of the mixed material.
    """
    C_hat = volf*C1 + (1-volf)*C2
    S_hat = np.linalg.inv(C_hat)
    return C_hat, S_hat


# Reuss limit of the rule of mixtures.
def reuss(S1, S2, volf):
    """
    Calculate the compliance matrix with the Reuss limit.
    This lower limit of the rule of mixtures is generaly used for the
    transverse stiffness :math:`E_l`.
    Parameters
    ----------
    S1 : matrix
        The compliance matrix of material 1.
    S2 : float
        The compliance matrix of material 2.
    volf : matrix
        The volume fraction of material 1.
    Returns
    -------
    C_hat : matrix
        The stiffess matrix of the mixed material.
    S_hat : matrix
        The compliance matrix of the mixed material.
    """
    S_hat = volf*S1 + (1-volf)*S2
    C_hat = np.linalg.inv(S_hat)
    return C_hat, S_hat