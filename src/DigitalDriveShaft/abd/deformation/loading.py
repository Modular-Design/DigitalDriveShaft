# Calculate the strain in the plate and curvature (Kirchhoff plate theory).
def load_applied(abd_inv, load):
    r"""
    Calculate the strain and curvature of the full plate under a given load using Kirchhoff plate theory.
    Parameters
    ----------
    abd : matrix
        The inverse of the ABD matrix.
    load : vector
        The load vector consits of are :math:`(N_x, N_y, N_{xy}, M_x, M_y, M_{xy})^T`
    Returns
    -------
    deformation : vector
        This deformation consists of :math:`(\varepsilon_x, \varepsilon_y
        \varepsilon_{xy},\kappa_x, \kappa_y, \kappa_{xy})^T`
    """
    deformation = abd_inv.dot(load)
    return deformation


# Calculate the running force & moment on the plate (Kirchhoff plate theory).
def deformation_applied(abd, deformation):
    r"""
    Calculate the running load and moment of the plate under a given using Kichhoff plate theory.
    Parameters
    ----------
    abd : matrix
        The ABD matrix.
    deformation : vector
        This deformation consists of :math:`(\varepsilon_x, \varepsilon_y,
        \varepsilon_{xy},\kappa_x, \kappa_y, \kappa_{xy})^T`
    Returns
    -------
    load : vector
        The load vector consits of are :math:`(N_x, N_y, N_{xy}, M_x, M_y, M_{xy})^T`
    """
    load = abd.dot(deformation)
    return load
