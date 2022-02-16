# Convert mass fractions into volume fractions.
def massfrac_to_volfrac(fm1, rho1, rho2):
    r"""
    Caluculate the volume fraction from the mass fraction.
    Parameters
    ----------
    fm1 : float
        The mass fraction of material 1 defined as, fm1 = massa 1 / massa
        total.
    rho1 : float
        The density of material 1.
    rho2 : float
        The density of material 2.
    Return
    ------
    fv1 : float
        The fraction material 1 is used in volume.
    fv2 : float
        The fraction material 2 is used in volume.
    """
    v1 = fm1 / rho1         # Volume occupied by material 1.
    v2 = (1 - fm1) / rho2   # Volume orrupied by material 2.
    fv1 = v1 / (v1 + v2)
    fv2 = v2 / (v1 + v2)
    return fv1, fv2


# Convert volume fraction into mass fractions.
def volfrac_to_massfrac(fv1, rho1, rho2):
    r"""
    Caluculate the mass fraction from the volume fraction.
    Parameters
    ----------
    fv1 : float
        The volume fraction of material 1 defined as, fv1 = volume 1 / volume
        total.
    rho1 : float
        The density of material 1.
    rho2 : float
        The density of material 2.
    Return
    ------
    fm1 : float
        The fraction material 1 is used in mass
    fm2 : float
        The fraction material 2 is used in mass.
    """
    fm1, fm2 = massfrac_to_volfrac(fv1, 1/rho1, 1/rho2)
    return fm1, fm2
