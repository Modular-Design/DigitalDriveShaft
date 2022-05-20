import numpy as np


# Test the Tsai-Hill Criteria for plane stress.
def tsai_hill(stress, sl_max, sl_min, st_max, st_min, tlt_max):
    """
    Test wether the stresses are outside the plane stress Tsai-Hill criteria.
    Failure stresses and ply stresses must be in the same orientation.
    The method is an extension of the von Mieses stress criteria.
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

    # Calculate the compression and tension maxima:
    slm = ((np.sign(sl)+1)/(2))*sl_max + ((np.sign(sl)-1)/(2))*sl_min
    stm = ((np.sign(st)+1)/(2))*st_max + ((np.sign(st)-1)/(2))*st_min

    # Applying the criteria itelf.
    Criteria = (sl/slm)**2 + (st/stm)**2 - (sl*st)/(slm**2)+(tlt/tlt_max)**2

    # Print a report if failure is occurs.
    if np.max(Criteria) > 1:
        error = np.where(Criteria > 1)
        print("The Tsai-Hill criteria was violated at:")
        for i in range(len(error[0])):
            print("    - The", loc[error[1][i]], "of layer", error[0][i]+1)
        return False

    return True
