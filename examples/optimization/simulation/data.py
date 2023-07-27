from ansys.mapdl.core import Mapdl, launch_mapdl  # noqa
from pymaterial.failures import CuntzeFailure
from pymaterial.materials import TransverselyIsotropicMaterial

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


material_legend = {
    "CFK": hts40_mat,
    "Alu": None,
    "GFK": None,
}

mapdl = Mapdl("127.0.0.1", port=50052)


def create_shaft(materials, shape, n_layers, thicknesses, angles):
    csp = CubicSpline(
        [0 * length, 0.5 * length, 1 * length],
        [d0 / 2, (d1 - d0) / 2 * (shape + 1.0), d1 / 2],
    )
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
