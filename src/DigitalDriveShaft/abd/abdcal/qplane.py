import numpy as np


# Determine the stiffness matrix for an in plane stress ply.
def QPlaneStress(El, Et, nult, G):
    r"""
    Generate the plane stress local stiffness matrix.
    Parameters
    ----------
    El : float
        Elastic modulus in the longitudional direction.
    Et : float
        Elastic modulus in the transverse direction.
    nult : float
        Poisson ratio in longitudional-transverse direction.
    G : float
        Shear modulus in longitudional-transverse directions.
    Returns
    -------
    Q : matrix
        Stiffness matrix in longitudional-transverse directions.
    """
    nutl = nult*Et/El
    Q = np.array([[El/(1-nult*nutl), (nult*Et)/(1-nult*nutl), 0],
                   [(nutl*El)/(1-nult*nutl), Et/(1-nult*nutl), 0],
                   [0, 0, G]])
    return Q


# Determine the stiffness matrix for an in plane strain ply.
def QPlaneStrain(El, Et, nult, G):
    r"""
    Generate the plane strain local stiffness matrix.
    .. warning::
        Not yet implemented.
        It raises a `NotImplementedError`.
    Parameters
    ----------
    El : float
        Elastic modulus in the longitudional direction.
    Et : float
        Elastic modulus in the transverse direction.
    nult : float
        Poisson ratio in longitudional-transverse direction.
    G : float
        Shear modulus in longitudional-transverse directions.
    Returns
    -------
    Q : matrix
        Stiffness matrix in longitudional-transverse directions.
    """
    nutl = nult * Et / El
    Q = np.array([[El / (1 - nult * nutl), (nult * Et) / (1 - nult * nutl), 0],
                   [(nutl * El) / (1 - nult * nutl), Et / (1 - nult * nutl), 0],
                   [0, 0, G]])
    raise NotImplementedError(
        'QPlaneStrain is undefined. Use plane stress version QPlaneStress.')
    return 0