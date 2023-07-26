from optuna import create_study
from pymaterial.materials import TransverselyIsotropicMaterial
from pymaterial.combis.clt import Ply, Stackup
from pymaterial.failures import CuntzeFailure
from scipy.interpolate import CubicSpline
from DigitalDriveShaft.analysis import Loading
from DigitalDriveShaft.cylindrical import (
    DriveShaft,
    CylindricalStackup,
    CylindricalForm,
)
from DigitalDriveShaft.sim.evaluation import (
    calc_buckling,  # noqa
    calc_eigenfreq,
    calc_strength,
)
from ansys.mapdl.core import launch_mapdl
from typing import Union, Sequence

# https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer

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

mapdl = launch_mapdl(mode="grpc", loglevel="ERROR")


def objective(trial) -> Union[float, Sequence[float]]:
    n_layers = 4  # trial.suggest_int("n_layers", 1, 6)
    shape = trial.suggest_float("shape", 0.0, 1.0)
    thicknesses = []
    angles = []
    materials = []

    for i in range(n_layers):
        thicknesses.append(trial.suggest_float(f"t{i}", 0.2, 4, step=0.2))
        angles.append(
            (
                trial.suggest_float(f"a{i}", -90.0, 90.0, step=1.0),
                trial.suggest_float(f"b{i}", -90.0, 90.0, step=1.0),
            )
        )
        materials.append(
            trial.suggest_categorical(f"material{i}", ["CFK"])  # , "Alu", "GFK"
        )

    csp = CubicSpline(
        [0 * length, 0.5 * length, 1 * length],
        [d0 / 2, (d1 - d0) / 2 * (shape + 1.0), d1 / 2],
    )
    cyl_form = CylindricalForm(lambda z, phi: csp(z), 500)

    def stackup_func(z: float, phi: float) -> Stackup:
        plies = []
        for i in range(n_layers):
            material = material_legend[materials[i]]
            start, end = angles[i]
            rotation = (end - start) * z + start
            plies.append(Ply(material, thicknesses[i], rotation, degree=True))
        return Stackup(plies)

    cyl_stackup = CylindricalStackup(stackup_func)
    shaft = DriveShaft(cyl_form, cyl_stackup)

    mass = shaft.get_mass()
    f_moment = calc_strength(mapdl, shaft, Loading(mz=M_max), dict())  # Nm
    f_force = calc_strength(mapdl, shaft, Loading(fz=N_max), dict())  # Nm
    # buck_moment = calc_buckling(mapdl, shaft, None, "MOMENT")[0] * 1000.0  # [Nm]
    rpm = calc_eigenfreq(mapdl, shaft, None)[0] * 60  # [RPM]
    # if buckling < 1.0:
    #     raise TrialPruned
    return mass, f_moment, f_force, rpm


study = create_study(
    study_name="simulation",
    storage="sqlite:///db.sqlite3",
    load_if_exists=True,
    directions=["minimize", "minimize", "minimize", "maximize"],
)
study.optimize(objective, n_trials=100)

# optuna-dashboard.exe sqlite:///examples/db.sqlite3
