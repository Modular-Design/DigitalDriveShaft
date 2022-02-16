from .orthotropic import orthotropic3D


# Transversly isotropic constitutive equation.
def trans_isotropic3D(E1, E2, nu12, nu23, G12):
    r"""
    Determine stiffness & compliance matrix of 3D transverse isotropic material.
    This notation is in Voigt notation with engineering strain
    :math:`\gamma_{12}=2\varepsilon_{12}`.
    Parameters
    ----------
    E1 : float
        Young's modulus in 1 direction.
    E3 : float
        Young's modulus in 3 direction.
    nu12 : float
        Poisson's ratio over 12.
    nu23 : float
        Poisson's ratio over 23.
    G13 : float
        Shear modulus over 13.
    Returns
    -------
    C : matrix
        2D stiffness matrix in Voigt notaion (6x6).
    S : matrix
        2D compliance matrix in Voigt notation (6x6).
    """
    E3 = E2
    nu13 = nu12
    G23 = E2/(2*(1 + nu23))
    G13 = G12
    C, S = orthotropic3D(E1, E2, E3, nu12, nu13, nu23, G12, G13, G23)
    return C, S


# Transversly isotropic constitutive equation in plane stress.
def trans_isotropic2D(E1, E2, nu12, G12):
    r"""
    Determine stiffness & compliance matrix of 2D plane stress transverse isotropic material.
    This notation is in Voigt notation with engineering strain
    :math:`\gamma_{12}=2\varepsilon_{12}`.
    Parameters
    ----------
    E1 : float
        Young's modulus in 1 direction.
    E2 : float
        Young's modulus in 3 direction.
    nu12 : float
        Poisson's ratio over 12.
    G12 : float
        Shear modulus over 13.
    Returns
    -------
    C : matrix
        2D stiffness matrix in Voigt notaion (3x3).
    S : matrix
        2D compliance matrix in Voigt notation (3x3).
    """
    S = np.matrix([[1/E1, -nu12/E1, 0],
                   [-nu12/E1, 1/E2, 0],
                   [0, 0, 1/(2*G12)]])
    C = np.linalg.inv(S)
    return C, S


# Isotropic constitutive equation.
def isotropic3D(E, nu):
    """
    Determine stiffness & compliance matrix of 3D isotropic material.
    Parameters
    ----------
    E : float
        Young's modulus.
    nu : float
        Poisson's ratio.
    Returns
    -------
    C : matrix
        3D stiffness matrix in Voigt notation (6x6).
    S : matrix
        3D compliance matrix in Voigt notation (6x6).
    """
    G = E/(2*(1 + nu))
    C, S = orthotropic3D(E, E, E, nu, nu, nu, G, G, G)
    return C, S


# Isotropic constitutive equation in plane stress.
def isotropic2D(E, nu):
    """
    Determine stiffness & compliance matrix of 2D isotropic material.
    Parameters
    ----------
    E : float
        Young's modulus.
    nu : float
        Poisson's ratio.
    Returns
    -------
    C : matrix
        3D stiffness matrix in Voigt notation (6x6).
    S : matrix
        3D compliance matrix in Voigt notation (6x6).
    """
    G = E/(2*(1 + nu))
    C, S = trans_isotropic2D(E, E, nu, G)
    return C, S