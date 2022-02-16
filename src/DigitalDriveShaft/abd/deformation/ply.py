import numpy as np
from .rotations import stress_rotation, strain_rotation
import matplotlib.pyplot as plt


# Calculate the strain in each ply.
def ply_strain(deformed, Q, angles, thickness):
    r"""
    Calculate the strain at the top and bottom of each ply.
    Small and linear deformations are assumed. For each ply two strain states
    are retured, one for the top and bottom of each ply. As bending moments can
    leed to different stresses depending on the :math:`z` location in the ply.
    Top plies should be listed first in the lists of Q, angles and thickness..
    Parameters
    ----------
    deformed : vector
        This deformation consists of :math:`(\varepsilon_x, \varepsilon_y
        \varepsilon_{xy},\kappa_x, \kappa_y, \kappa_{xy})^T`
    Q : list
        The local stiffness matrix of each ply.
    angles : list
        The rotation of each ply in degrees.
    thickness : list
        The thickness of each ply.
    plotting : bool, optional
        Plotting the stress distribution or not.
    Returns
    -------
    strain : list
        The stress vector :math:`(\sigma_{xx}, \sigma_{yy}, \tau_{xy})^T` of
        the top, middle and bottom of each ply in the laminate.
    """
    # Calculating total thickness of the layup.
    h = np.sum(thickness) / 2

    # Create a list for the strains in each ply.
    strain = []

    # Iterate over all plies.
    for i in range(len(thickness)):
        # Calculate the z coordinates of the top and bottom of the ply.
        z_top = np.sum(thickness[:i]) - h
        z_bot = np.sum(thickness[:i+1]) - h

        # Calculate deformation of the midplane of the laminate.
        strain_membrane = deformed[:3]
        curvature = deformed[3:]

        # Caluclate strain in the ply.
        strain_top = strain_membrane + z_top * curvature
        strain_bot = strain_membrane + z_bot * curvature

        # Rotate strain from global to ply axis sytstem.
        strain_lt_top = strain_rotation(strain_top, -angles[i])
        strain_lt_bot = strain_rotation(strain_bot, -angles[i])

        # Store the strain values of this ply.
        strain_ply = [strain_lt_top, strain_lt_bot]
        strain.append(strain_ply)

    return strain


# Calculate the stress in each ply.
def ply_stress(deformed, Q, angles, thickness, plotting=False):
    r"""
    Calculate the stresses at the top and bottom of each ply.
    Small and linear deformations are assumed. For each ply two stress states
    are retured, one for the top and bottom of each ply. As bending moments can
    leed to different stresses depending on the :math:`z` location in the ply.
    Top plies should be listed first in the lists of Q, angles and thickness.
    If required the stresses can be plotted as a function of the :math:`z`
    coordinates. In this plot the stresses shown are in the global axsis
    system :math:`x` and :math:`y`.
    Parameters
    ----------
    deformed : vector
        This deformation consists of :math:`(\varepsilon_x, \varepsilon_y
        \varepsilon_{xy},\kappa_x, \kappa_y, \kappa_{xy})^T`
    Q : list
        The local stiffness matrix of each ply.
    angles : list
        The rotation of each ply in degrees.
    thickness : list
        The thickness of each ply.
    plotting : bool, optional
        Plotting the through thickness stress distribution or not.
    Returns
    -------
    stress : list
        The stress vector :math:`(\sigma_{xx}, \sigma_{yy}, \tau_{xy})^T` of
        the top, middle and bottom of each ply in the laminate.
    """
    # Calculate the strain in local ply axes system.
    strain = ply_strain(deformed, Q, angles, thickness)

    # Create a list for the stresses in each ply.
    stress = []

    # Create an empty list of z coordinates and stresss for the plotting.
    if plotting is True:
        h = np.sum(thickness)/2
        z = []
        sigma_xx = []
        sigma_yy = []
        tau_xy = []

    # Iterate over all plies.
    for i in range(len(thickness)):
        # Obtain the strains from this ply.
        strain_lt_top = strain[i][0]
        strain_lt_bot = strain[i][1]

        # Convert strains into stresses.
        stress_lt_top = Q[i].dot(strain_lt_top)
        stress_lt_bot = Q[i].dot(strain_lt_bot)

        # Store the stress values of this ply.
        stress_ply = [stress_lt_top, stress_lt_bot]
        stress.append(stress_ply)

        # Add the coordinates and stresses of this ply to plotting lists.
        if plotting is True:
            # Calculate the z coordinates of the top and bottom of the ply.
            z_top = np.sum(thickness[:i]) - h
            z_bot = np.sum(thickness[:i+1]) - h
            z += [z_top, z_bot]

            # Rotate the stresses to the global axis system.
            stress_xy_top = stress_rotation(stress_lt_top, angles[i])
            stress_xy_bot = stress_rotation(stress_lt_bot, angles[i])
            sigma_xx += [stress_xy_top.item(0), stress_xy_bot.item(0)]
            sigma_yy += [stress_xy_top.item(1), stress_xy_bot.item(1)]
            tau_xy += [stress_xy_top.item(2), stress_xy_bot.item(2)]

    # Plot the stresses through the laminate thickness if requested.
    if plotting is True:
        plt.subplot(1, 3, 1)
        plt.plot(sigma_xx, z)
        plt.xlabel(r"Stress $\sigma_{xx}$")
        plt.ylabel(r"Location along $z$")
        plt.ylim((min(z), max(z)))
        ax = plt.gca()
        ax.invert_yaxis()

        plt.subplot(1, 3, 2)
        plt.plot(sigma_yy, z)
        plt.xlabel(r"Stress $\sigma_{yy}$")
        plt.ylim((min(z), max(z)))
        ax = plt.gca()
        ax.invert_yaxis()

        plt.subplot(1, 3, 3)
        plt.plot(tau_xy, z)
        plt.xlabel(r"Stress $\tau_{xy}$")
        plt.ylim((min(z), max(z)))
        ax = plt.gca()
        ax.invert_yaxis()

        plt.tight_layout()
        plt.show()

    return stress


# Calculate stress caused by thermal  strains.
def ply_stress_thermal(deformed, angles, Q, thickness, alpha, dT):
    r"""
    Calculate the stress due to mechanical and thermal deformation.
    Parameters
    ----------
    deformed : vector
        This deformation of the entire laminate. :math:`(\varepsilon_x,
        \varepsilon_y, \varepsilon_{xy},\kappa_x, \kappa_y, \kappa_{xy})^T`
    Q : list
        The local stiffness matrix of each ply in l-t axis system.
    angles : list
        The rotation of each ply in degrees.
    thickness : list
        The thickness of each ply.
    alpha : list
        The coeficcient of termal expansion of each ply in l-t axis system.
    dT : float
        Change in temperature.
    Returns
    -------
    stress : list
        The stress vector :math:`(\sigma_{xx}, \sigma_{yy}, \tau_{xy})^T` of
        the top, middle and bottom of each ply in the laminate.
    """
    # Calculate the strain in local ply axes system.
    strain = ply_strain(deformed, Q, angles, thickness)

    # Create a list for the stresses in each ply.
    stress = []

    # Iterate over all plies.
    for i in range(len(thickness)):
        # Obtain the strains in this ply including the termal terms.
        strain_lt_top = strain[i][0] - dT * alpha[i]
        strain_lt_bot = strain[i][1] - dT * alpha[i]

        # Convert strains into stresses.
        stress_lt_top = Q[i].dot(strain_lt_top)
        stress_lt_bot = Q[i].dot(strain_lt_bot)

        # Store the stress values of this ply.
        stress_ply = [stress_lt_top, stress_lt_bot]
        stress.append(stress_ply)

    return stress