from optuna import create_study, samplers, TrialPruned
from pymaterial.materials import TransverselyIsotropicMaterial
from pymaterial.combis.clt import Ply, Stackup
from pymaterial.failures import CuntzeFailure
from scipy.interpolate import CubicSpline
from DigitalDriveShaft.cylindrical import (
    CylindricalStackup,
    CylindricalForm,
    DriveShaft,
)
from DigitalDriveShaft.analysis import (
    calc_crit_moment,
    calc_crit_rpm,
    get_relevant_value,
    calc_static_porperties,
    Loading,
)
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
    density=1.58,  # kg/mm^3
    failures=[hts40_cuntze],
)  # MPa


material_legend = {
    "CFK": hts40_mat,
    "Alu": None,
    "GFK": None,
}


def objective(trial) -> Union[float, Sequence[float]]:
    n_layers = 4  # = trial.suggest_int("n_layers", 1, 6)
    shape = trial.suggest_float("shape", -0.2, 1.0)

    thicknesses = []
    angles = []
    materials = []

    for i in range(n_layers):
        thicknesses.append(trial.suggest_float(f"t{i}", 0.2, 4, step=0.2))
        angles.append(trial.suggest_float(f"a{i}", -90.0, 90.0, step=1.0))
        materials.append(
            trial.suggest_categorical(f"material{i}", ["CFK"])  # , "Alu", "GFK"
        )

    plies = []
    for i in range(n_layers):
        material = material_legend[materials[i]]
        plies.append(Ply(material, thicknesses[i], angles[i], degree=True))
    stackup = Stackup(plies)

    csp = CubicSpline(
        [0 * length, 0.5 * length, 1 * length],
        [d0 / 2, (d1 - d0) / 2 * (shape + 1.0), d1 / 2],
    )
    cyl_form = CylindricalForm(lambda z, phi: csp(z), 500)
    cyl_stack = CylindricalStackup(lambda z, phi: stackup)

    shaft = DriveShaft(form=cyl_form, stackup=cyl_stack)
    mass = shaft.get_mass()
    _, _, failures = calc_static_porperties(shaft, Loading(mz=M_max))  # Nm
    f_moment = get_relevant_value(failures)  # auslastung

    _, _, failures = calc_static_porperties(shaft, Loading(fz=N_max))  # N
    f_force = get_relevant_value(failures)  # auslastung

    buckling = calc_crit_moment(shaft)
    rpm = calc_crit_rpm(shaft)

    c_moment = f_moment - 1.0  # has to be smaller 1
    c_force = f_force - 1.0  # has to be smaller 1
    c_rpm = rpm_min - rpm  # has to be larger 6000 rpm

    trial.set_user_attr("constraint", (c_moment, c_force, c_rpm))
    if f_moment > 5.0 or f_force > 5.0:
        raise TrialPruned()
    if rpm < rpm_min * 0.2:
        raise TrialPruned()
    return mass, buckling, rpm, f_moment, f_force


def constraints(trial):
    return trial.user_attrs["constraint"]


study = create_study(
    study_name="analytic",
    storage="sqlite:///db.sqlite3",
    load_if_exists=True,
    directions=["minimize", "maximize", "maximize", "minimize", "minimize"],
    sampler=samplers.NSGAIIISampler(
        # constraints_func=constraints
    ),
)
study.optimize(objective, n_trials=1000)

# optuna-dashboard sqlite:///db.sqlite3
