import numpy as np


# Rotate stress vertor over given angle.
def stress_rotation(stress, angle):
    """
    Rotates a stress vector against a given angle.
    This rotates the stress from local to the global axis sytem.
    Use a negative angle to rotate from global to local system.
    The stress vector must be in Voigt notation and engineering stress is used.
    Parameters
    ----------
    stress : vector
        The matrix that must be rotated.
    angle : float
        The rotation angle in degrees.
    Returns
    -------
    stress_rot : vector
        A rotated version of the matrix.
    """
    angle = angle * np.pi/180  # convert to radians
    m = np.cos(-angle)
    n = np.sin(-angle)
    T1_inv = np.matrix([[m**2, n**2, 2*m*n],
                        [n**2, m**2, -2*m*n],
                        [-m*n, m*n, m**2-n**2]])
    stress_rot = T1_inv * stress
    return stress_rot


# Rotate strain vector over given angle.
def strain_rotation(strain, angle):
    """
    Rotates a strain vector against a given angle.
    This rotates the strain from local to the global axis sytem.
    Use a negative angle to rotate from global to local system.
    The strain vector must be in Voigt notation and engineering strain is used.
    Parameters
    ----------
    strain : vector
        The matrix that must be rotated.
    angle : float
        The rotation angle in degrees.
    Returns
    -------
    strain_rot : vector
        A rotated version of the matrix.
    """
    angle = angle * np.pi/180  # convert to radians
    m = np.cos(-angle)
    n = np.sin(-angle)
    T2_inv = np.matrix([[m**2, n**2, m*n],
                        [n**2, m**2, -m*n],
                        [-2*m*n, 2*m*n, m**2-n**2]])
    strain_rot = T2_inv * strain
    return strain_rot
