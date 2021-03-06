import numpy as np


# Test the Tsai-Wu Criteria.
def tsai_wu(stress, sl_max, sl_min, st_max, st_min, tlt_max):
    """
    Test wether the stresses are outside the plane stress Tsai-Wu criteria.
    Failure stresses and ply stresses must be in the same orientation.
    .. warning::
        This criteria is a bad approximation for compression failure.
    Parameters
    ----------
    stress : list
        A list containing the stress vector of the bottom, middle
        and top of each layer.
    sl_max : float
        Maximum tensile stress in longitudional direction.
    sl_min : float
        Maximum compressive stress in longitudional direction.
    st_max : float
        Maximum tensile stress in transverse direction.
    st_min : float
        Maximum compressive stress in transverse direction.
    tlt_max : float
        Maximum shear stress in material axis system.
    Returns
    -------
    pass : bool
        True if the load was below the maximum allowables.
    """
    # Name location inside stress vectors in each ply.
    loc = ['top', 'bottom']

    # Separate the stress components of the plies.
    sl = np.array(stress)[:, :, 0, 0]
    st = np.array(stress)[:, :, 1, 0]
    tlt = np.array(stress)[:, :, 2, 0]

    # Calculate the constants for Tsai-Wu Criteria.
    f1 = 1 / sl_max - 1 / sl_min
    f11 = 1 / (sl_min * sl_min)
    f2 = 1 / st_max - 1 / st_min
    f22 = 1 / (st_max * st_min)
    f66 = 1 / tlt_max**2
    f12 = -1/2 * np.sqrt(f11 * f22)  # This is an approximation

    # Apply the criteria itself.
    criteria = -f1*sl + f2*st + f11*sl**2 + f22*st**2 + f66*tlt**2 + 2*f12*sl*st

    # Print a report if failure is occurs.
    if np.max(criteria) > 1:
        error = np.where(criteria > 1)
        print("The Tsai-Wu criteria was violated at:")
        for i in range(len(error[0])):
            print("    - The", loc[error[1][i]], "of layer", error[0][i]+1)
        return False

    return True
