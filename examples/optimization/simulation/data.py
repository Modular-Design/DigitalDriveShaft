from ansys.mapdl.core import Mapdl, launch_mapdl  # noqa
from pymaterial.failures import CuntzeFailure, VonMisesFailure
from pymaterial.materials import TransverselyIsotropicMaterial, IsotropicMaterial

from pymaterial.combis.clt import Ply, Stackup

from scipy.interpolate import CubicSpline
from DigitalDriveShaft.cylindrical import (
    DriveShaft,
    CylindricalStackup,
    CylindricalForm,
)

d0 = 0.170  # m
d1 = 0.340  # m
length = 0.500  # m
M_max = 160e3  # Nm
N_max = -2e3  # N
rpm_min = 6000  # rpm

# CFK UD(230 GPa) prepreg (source: ANSYS composite engineering data)
CFK_230GPa_prepreg_cuntze = CuntzeFailure(
    E1=121000e6,  # Pa
    R_1t=2231.0e6,
    R_1c=1082e6,  # Pa
    R_2t=29e6,
    R_2c=100e6,  # Pa
    R_21=60e6,  # Pa
    my_21=0.27,
)

CFK_230GPa_prepreg = TransverselyIsotropicMaterial(
    E_l=121000e6,  # Pa
    E_t=8600e6,  # Pa
    nu_lt=0.27,
    nu_tt=0.4,
    G_lt=4700e6,  # Pa
    density=1490,  # kg/m^3
    failures=[CFK_230GPa_prepreg_cuntze],
)  # MPa


# Stainless steel 316 (source: Granta DB)
steel_mises = VonMisesFailure(252e6)  # Pa

steel = IsotropicMaterial(
    Em=195000e6, nu=0.27, density=7969, failures=[steel_mises]  # Pa
)

# Titan alloy Ti-6Al-4V (source: Granta DB)

titan_mises = VonMisesFailure(845.7e6)

titan = IsotropicMaterial(
    Em=111200e6, nu=0.3387, density=4429, failures=[titan_mises]  # Pa  # kg/m^3
)

material_legend = {
    "CFK": CFK_230GPa_prepreg,
    "Steel": steel,
    "Titanium": titan,
}

mapdl = Mapdl("127.0.0.1", port=50052)
# MKS - MKS system (m, kg, s, °C)
mapdl.units("MKS")


def create_shape_func(shape):
    csp = CubicSpline(
        [0 * length, 0.5 * length, 1 * length],
        [d0 / 2, (d1 - d0) / 2 * (shape + 1.0), d1 / 2],
        bc_type=((1, 0.0), (1, 0.0)),
    )
    return csp


def create_shaft(materials, shape, n_layers, thicknesses, angles):
    csp = create_shape_func(shape)
    cyl_form = CylindricalForm(lambda z, phi: csp(z), 500)

    def stackup_func(z: float, phi: float) -> Stackup:
        plies = []
        for i in range(n_layers):
            material = material_legend[materials[i]]
            # start, end = angles[i]
            # rotation = (end - start) * z + start
            plies.append(Ply(material, thicknesses[i], angles[i], degree=True))
        return Stackup(plies)

    cyl_stackup = CylindricalStackup(stackup_func)
    shaft = DriveShaft(cyl_form, cyl_stackup)
    return shaft


# Show driveshaft shapes
"""
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, length, 1000)
y = create_shape_func(0.2)(x)
fig, ax = plt.subplots(figsize=(6.5, 4))

ax.plot(x, y, label='data')
plt.show()
"""
