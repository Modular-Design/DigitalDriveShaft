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

d0 = 170  # mm
d1 = 340  # mm
length = 500  # mm
M_max = 160e3 * 1e3  # Nm
N_max = -2e3  # N
rpm_min = 6000  # rpm


hts40_cuntze = CuntzeFailure(
    E1=145200, R_1t=852.0, R_1c=631, R_2t=57, R_2c=274, R_21=132  # MPa  # MPa  # MPa
)

hts40_mat = TransverselyIsotropicMaterial(
    E_l=145200,  # MPa
    E_t=6272.7,  # MPa
    nu_lt=0.28,  # MPa
    G_lt=2634.2,  # MPa
    density=1.58,  # g/cm^3 -> 1e-6 kg/mm^3
    failures=[hts40_cuntze],
)  # MPa


# Stainless steel 316 (source: Granta DB)
steel_mises = VonMisesFailure(252)

steel = IsotropicMaterial(Em=195000, nu=0.27, density=7.969, failures=[steel_mises])

# Titan alloy Ti-6Al-4V (source: Granta DB)

titan_mises = VonMisesFailure(845.7)

titan = IsotropicMaterial(Em=111200, nu=0.3387, density=4.429, failures=[titan_mises])

material_legend = {
    "CFK": hts40_mat,
    "Steel": steel,
    "Titan": titan,
}

mapdl = Mapdl("127.0.0.1", port=50052)


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
