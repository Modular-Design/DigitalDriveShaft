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

mapdl = Mapdl("127.0.0.1", port=50052)
# https://mapdl.docs.pyansys.com/version/stable/mapdl_commands/database/_autosummary/ansys.mapdl.core.Mapdl.units.html
# MKS - MKS system (m, kg, s, °C)
# MPA - MPA system (mm, Mg = t, s, °C)
# MPA is required, because small scale details are hard to model in [m]
mapdl.units("MPA")


d0 = 170  # mm
d1 = 340  # mm
length = 500  # mm
M_max = 160e3 * 1e3  # Nm = 1 kg*m^2*s^2 -> 1e3 t*mm^2/s^2
N_max = -2e3  # N = 1 kg*m*s^2 -> 1 t*mm/s^2
rpm_min = 6000  # rpm

# CFK UD(230 GPa) prepreg (source: ANSYS composite engineering data)
CFK_230GPa_prepreg_cuntze = CuntzeFailure(
    E1=121000,  # t/s^2/mm
    R_1t=2231.0,  # t/s^2/mm
    R_1c=1082,  # t/s^2/mm
    R_2t=29,  # t/s^2/mm
    R_2c=100,  # t/s^2/mm
    R_21=60,  # t/s^2/mm
    my_21=0.27,
)

CFK_230GPa_prepreg = TransverselyIsotropicMaterial(
    E_l=121000,  # t/s^2/mm
    E_t=8600,  # t/s^2/mm
    nu_lt=0.27,
    nu_tt=0.4,
    G_lt=4700,  # t/s^2/mm
    density=1.490e-9,  # t/mm^3
    failures=[CFK_230GPa_prepreg_cuntze],
)  # MPa

# CFK UD(395 GPa) prepreg (source: ANSYS composite engineering data)
CFK_395GPa_prepreg_cuntze = CuntzeFailure(
    E1=121000,  # t/s^2/mm
    R_1t=1979,  # t/s^2/mm
    R_1c=893,  # t/s^2/mm
    R_2t=26,  # t/s^2/mm
    R_2c=139,  # t/s^2/mm
    R_21=100,  # t/s^2/mm
    my_21=0.27,
)

CFK_395GPa_prepreg = TransverselyIsotropicMaterial(
    E_l=209000,  # t/s^2/mm
    E_t=9450,  # t/s^2/mm
    nu_lt=0.27,
    nu_tt=0.4,
    G_lt=5500,  # t/s^2/mm
    density=1.54e-09,  # t/mm^3
    failures=[CFK_230GPa_prepreg_cuntze],
)  # MPa

# Epoxy E-Glass UD (source: ANSYS composite engineering data)
GFK_cuntze = CuntzeFailure(
    E1=45000,  # t/s^2/mm
    R_1t=1100,  # t/s^2/mm
    R_1c=675,  # t/s^2/mm
    R_2t=35,  # t/s^2/mm
    R_2c=120,  # t/s^2/mm
    R_21=80,  # t/s^2/mm
    my_21=0.3,
)

GFK_prepreg = TransverselyIsotropicMaterial(
    E_l=45000,  # t/s^2/mm
    E_t=10000,  # t/s^2/mm
    nu_lt=0.3,
    nu_tt=0.4,
    G_lt=5000,  # t/s^2/mm
    density=2e-09,  # t/mm^3
    failures=[CFK_230GPa_prepreg_cuntze],
)  # MPa

# Stainless steel 316 (source: Granta DB)
steel_mises = VonMisesFailure(252.1)  # Pa

steel = IsotropicMaterial(
    Em=195000, nu=0.27, density=7.969e-9, failures=[steel_mises]  # t/s^2/mm  # t/mm^3
)

# Titan alloy Ti-6Al-4V (source: Granta DB)

titan_mises = VonMisesFailure(845.7)  # t/s^2/mm

titan = IsotropicMaterial(
    Em=111200, nu=0.3387, density=4.429e-9, failures=[titan_mises]  # t/s^2/mm  # t/mm^3
)

material_legend = {
    r"CFK_{230}": CFK_230GPa_prepreg,
    r"CFK_{395}": CFK_395GPa_prepreg,
    "GFK": GFK_prepreg,
    "Steel": steel,
    "Titanium": titan,
}


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
