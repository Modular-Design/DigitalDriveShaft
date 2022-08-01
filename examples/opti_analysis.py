from optuna import create_study, TrialPruned
from src.DigitalDriveShaft.basic import TransverselyIsotropicMaterial, Ply, Stackup, Loading, CuntzeFailure
from src.DigitalDriveShaft.cylindrical import SimpleDriveShaft
from src.DigitalDriveShaft.analysis import calc_buckling, calc_dynamic_stability
from typing import Union, Sequence

# https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer

hts40_cuntze = CuntzeFailure(
                                E1=145200,  # MPa
                                R_1t=852.0, R_1c=631,  # MPa
                                R_2t=57, R_2c=274, R_21=132     # MPa
                            )

hts40_mat = TransverselyIsotropicMaterial(E_l=145200,  # MPa
                                          E_t=6272.7,  # MPa
                                          nu_lt=0.28,  # MPa
                                          G_lt=2634.2,  # MPa
                                          density=1.58,  # kg/mm^3
                                          failures=[hts40_cuntze])  # MPa


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
        thicknesses.append(trial.suggest_float(f't{i}', 0.2, 4, step=0.2))
        angles.append(trial.suggest_float(f'a{i}', -90.0, 90.0, step=1.0))
        materials.append(trial.suggest_categorical(f'material{i}', ["CFK"]))  # , "Alu", "GFK"

    plies = []
    for i in range(n_layers):
        material = material_legend[materials[i]]
        plies.append(Ply(material, thicknesses[i], angles[i], degree=True))
    stackup = Stackup(plies)

    shaft = SimpleDriveShaft(20, 500, stackup)
    mass = shaft.get_mass()
    buckling = calc_buckling(shaft, Loading(mz=168960))
    rpm = calc_dynamic_stability(shaft, Loading(mz=168960, rpm=6600))
    # if buckling < 1.0:
    #     raise TrialPruned
    return mass, buckling, rpm


study = create_study(
    study_name="analytic_no_pruning",
    storage="sqlite:///db.sqlite3",
    directions=["minimize", "maximize", "maximize"])
study.optimize(objective, n_trials=10)

# optuna-dashboard sqlite:///db.sqlite3