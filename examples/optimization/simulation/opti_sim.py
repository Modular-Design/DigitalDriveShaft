from data import mapdl, create_shaft, M_max, N_max, rpm_min
from DigitalDriveShaft.analysis import Loading
from DigitalDriveShaft.sim.evaluation import (
    calc_buckling,  # noqa
    calc_eigenfreq,
    calc_strength,
    calc_bending,
)
import numpy as np
from optuna import create_study
from typing import Union, Sequence


def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]


# https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer

# launch_mapdl(mode="grpc", loglevel="ERROR")

material_selection = []  # possible content: "CFK", "Steel", "Titan"


def objective(trial) -> Union[float, Sequence[float]]:
    n_layers = 4  # trial.suggest_int("n_layers", 1, 6)
    shape = trial.suggest_float("shape", 0.0, 1.0)
    thicknesses = []
    angles = []
    materials = []

    for i in range(n_layers):
        thicknesses.append(trial.suggest_float(f"t{i}", 1.2e-3, 5.2e-3, step=0.4e-3))
        angles.append(
            trial.suggest_float(f"a{i}", -90.0, 90.0, step=1.0),
        )
        materials.append(trial.suggest_categorical(f"material{i}", material_selection))

    shaft = create_shaft(materials, shape, n_layers, thicknesses, angles)
    mass = shaft.get_mass()

    f_moment = calc_strength(mapdl, shaft, Loading(mz=M_max), dict())  # Nm
    f_force = calc_strength(mapdl, shaft, Loading(fz=N_max), dict())  # Nm

    # buck_moment = calc_buckling(mapdl, shaft, None, "MOMENT")[0] * 1000.0  # [Nm]

    rpms = np.array(calc_eigenfreq(mapdl, shaft, None)) * 60  # [RPM]
    rpm = find_nearest(rpms, rpm_min)

    deform = calc_bending(mapdl, shaft, None)

    trial.set_user_attr("utilization", (f_moment, f_force))
    trial.set_user_attr("rpm", rpm)
    return mass, max(f_moment, f_force), np.abs(rpm - rpm_min), deform


study = create_study(
    study_name="simulation_metal",
    storage="sqlite:///db.sqlite3",
    load_if_exists=True,
    directions=["minimize", "minimize", "maximize", "maximize"],
)
material_selection = ["Steel", "Titanium"]
study.optimize(objective, n_trials=400)

study = create_study(
    study_name="simulation_composite",
    storage="sqlite:///db.sqlite3",
    load_if_exists=True,
    directions=["minimize", "minimize", "maximize", "maximize"],
)
material_selection = ["CFK", "Titanium"]
study.optimize(objective, n_trials=400)

# optuna-dashboard.exe sqlite:///examples/db.sqlite3
