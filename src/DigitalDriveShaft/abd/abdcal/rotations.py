import numpy as np


# Rotate the stiffness matrix over a given angle.
def stiffness_rotation(stiffness, angle):
    r"""
    Rotate the stiffness matrix against given angle.
    This rotates the stiffness matrix from local to the global axis sytem.
    Use a negative angle to rotate from global to local system.
    Parameters
    ----------
    stiffness : matrix
        The matrix that must be rotated.
    angle : float
        The rotation angle in degrees.
    Returns
    -------
    stiffness_rot : matrix
        A rotated version of the matrix.
    """
    angle = angle * np.pi/180  # convert to radians
    m = np.cos(angle)
    n = np.sin(angle)
    T1 = np.matrix([[m**2, n**2, 2*m*n],
                    [n**2, m**2, -2*m*n],
                    [-m*n, m*n, m**2-n**2]])
    T2 = np.matrix([[m**2, n**2, m*n],
                    [n**2, m**2, -m*n],
                    [-2*m*n, 2*m*n, m**2-n**2]])
    stiffness_rot = np.linalg.inv(T1) * stiffness * T2
    return stiffness_rot


# Rotate the compliance matrix over a given angle.
def compliance_rotation(compliance, angle):
    r"""
    Rotate the compliance matrix over a given angle.
    This rotates the complianc matrix from local to the global axis sytem.
    Use a negative angle to rotate from global to local system.
    Parameters
    ----------
    compliance : matrix
        The matrix that must be rotated.
    angle : float
        The rotation angle in degrees.
    Returns
    -------
    stiffness_rot : matrix
        A rotated version of the matrix.
    """
    angle = angle * np.pi/180  # convert to radians
    m = np.cos(angle)
    n = np.sin(angle)
    T1 = np.matrix([[m**2, n**2, 2*m*n],
                    [n**2, m**2, -2*m*n],
                    [-m*n, m*n, m**2-n**2]])
    T2 = np.matrix([[m**2, n**2, m*n],
                    [n**2, m**2, -m*n],
                    [-2*m*n, 2*m*n, m**2-n**2]])
    compliance_rot = np.linalg.inv(T2) * compliance * T1
    return compliance_rot