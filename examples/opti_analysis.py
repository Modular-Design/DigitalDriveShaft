from optuna import create_study
from pymaterial.materials import TransverselyIsotropicMaterial
from pymaterial.combis.clt import Ply, Stackup
from pymaterial.failures import CuntzeFailure
from src.DigitalDriveShaft.cylindrical import SimpleDriveShaft
from src.DigitalDriveShaft.analysis import (
    calc_crit_moment,
    calc_crit_rpm,
    get_relevant_value,
    calc_static_porperties,
    Loading,
)
from typing import Union, Sequence

# https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer

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
    n_layers = trial.suggest_int("n_layers", 1, 6)
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

    shaft = SimpleDriveShaft(20, 500, stackup)
    mass = shaft.get_mass()
    _, _, failures = calc_static_porperties(shaft, Loading(mz=1e3))  # Nm
    cuntze = get_relevant_value(failures)  # auslastung
    buckling = calc_crit_moment(shaft)
    rpm = calc_crit_rpm(shaft)
    # if cuntze > 1.0:
    #     raise TrialPruned
    # if buckling < 1.0:
    #     raise TrialPruned
    return mass, cuntze, buckling, rpm


study = create_study(
    study_name="analytic",
    storage="sqlite:///db.sqlite3",
    load_if_exists=True,
    directions=["minimize", "minimize", "maximize", "maximize"],
)
study.optimize(objective, n_trials=10000)

# optuna-dashboard sqlite:///db.sqlite3
