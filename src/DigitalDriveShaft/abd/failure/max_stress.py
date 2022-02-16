import numpy as np


# Test the max stress failure.
def max_stress(stress, sl_max, sl_min, st_max, st_min, tlt_max):
    """
    Compare stresses to the max stress criteria, returns which layers failed.
    Failure stresses and ply stresses must be in the same orientation.
    .. warning::
        This method does not take interaction of stresses in different
        directions in account.
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

    # Check if anything fails, value is True if it is outside the criteria.
    sl_tens = np.any(sl >= sl_max)
    sl_comp = np.any(-sl_min >= sl)
    st_tens = np.any(st >= st_max)
    st_comp = np.any(-st_min >= st)
    shear = np.any(np.abs(tlt) >= tlt_max)

    # Print a report if failure is occurs.
    if any([sl_tens, sl_comp, st_tens, st_comp, shear]):
        print("The max stress criteria was violated at:")

        if np.max(sl) >= sl_max:
            error = np.unravel_index(np.argmax(sl, axis=None), sl.shape)
            print('    - Max longitudional tension at the', loc[error[1]], 'of Layer', error[0]+1)
        if np.min(sl) <= -sl_min:
            error = np.unravel_index(np.argmin(sl, axis=None), sl.shape)
            print('    - Max longitudional compression at the', loc[error[1]], 'of Layer', error[0]+1)
        if np.max(st) >= st_max:
            error = np.unravel_index(np.argmax(st, axis=None), st.shape)
            print('    - Max transverse tension at the', loc[error[1]], 'of Layer', error[0]+1)
        if np.min(st) <= -st_min:
            error = np.unravel_index(np.argmin(st, axis=None), st.shape)
            print('    - Max transverse compression at the', loc[error[1]], 'of Layer', error[0]+1)
        if np.max(np.abs(tlt)) >= tlt_max:
            error = np.unravel_index(np.argmax(tlt, axis=None), tlt.shape)
            print('    - Max Shear failure at the', loc[error[1]], 'Layer', error[0]+1)

        return False

    return True
