# Orthotropic constitutive equation.
def orthotropic3D(E1, E2, E3, nu12, nu13, nu23, G12, G13, G23):
    r"""
    Determine stiffness & compliance matrix of a 3D orthotropic material.
    This notation is in Voigt notation with engineering strain
    :math:`\gamma_{12}=2\varepsilon_{12}`.
    Parameters
    ----------
    E1 : float
        Young's modulus in 1 direction.
    E2 : float
        Young's modulus in 2 direction.
    E3 : float
        Young's modulus in 3 direction.
    nu12 : float
        Poisson's ratio over 12.
    nu13 : float
        Poisson's ratio over 13.
    nu23 : float
        Poisson's ratio over 23.
    G12 : float
        Shear modulus over 12.
    G13 : float
        Shear modulus over 13.
    G23 : float
        Shear modulus over 23.
    Returns
    -------
    C : matrix
        2D stiffness matrix in Voigt notaion (6x6).
    S : matrix
        2D compliance matrix in Voigt notation (6x6).
    """
    S = np.matrix([[1/E1, -nu12/E1, -nu13/E1, 0, 0, 0],
                   [-nu12/E1, 1/E2, -nu23/E2, 0, 0, 0],
                   [-nu13/E1, -nu23/E2, 1/E3, 0, 0, 0],
                   [0, 0, 0, 1/G12, 0, 0],
                   [0, 0, 0, 0, 1/G13, 0],
                   [0, 0, 0, 0, 0, 1/G23]])
    C = np.linalg.inv(S)
    return C, S