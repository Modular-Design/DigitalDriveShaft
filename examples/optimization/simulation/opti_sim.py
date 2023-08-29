from data import mapdl, create_shaft, M_max, N_max, rpm_min
from DigitalDriveShaft.analysis import Loading
from DigitalDriveShaft.sim.evaluation import (
    calc_deformation,
    calc_eigenfreq,
    calc_strength,
)
import numpy as np
from optuna import create_study, samplers
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

    thicknesses = trial.suggest_float("t", 12.0, 18.0, step=0.4)

    for i in range(n_layers):
        angles.append(
            trial.suggest_float(f"a{i}", -60.0, 60.0, step=1.0),
        )
        materials.append(trial.suggest_categorical(f"material{i}", material_selection))

    shaft = create_shaft(materials, shape, n_layers, thicknesses, angles)
    mass = shaft.get_mass()

    f_moment_1 = calc_strength(
        mapdl,
        shaft,
        Loading(mz=-1.0 * M_max),
        dict(n_phi=16, n_z=10, extensions=(int(500 / 10 * 3), int(500 / 10 * 3))),
    )
    f_moment_2 = calc_strength(
        mapdl,
        shaft,
        Loading(mz=-1.0 * M_max),
        dict(n_phi=16, n_z=10, extensions=(int(500 / 10 * 3), int(500 / 10 * 3))),
    )
    f_force = calc_strength(
        mapdl,
        shaft,
        Loading(fz=N_max),
        dict(n_phi=16, n_z=10, extensions=(int(500 / 10 * 3), int(500 / 10 * 3))),
    )

    # buck_moment = calc_buckling(mapdl, shaft, None, "MOMENT")[0] * 1000.0  # [Nm]

    rpms = np.array(calc_eigenfreq(mapdl, shaft, dict())) * 60  # [RPM]
    rpm = find_nearest(rpms, rpm_min)

    deform = calc_deformation(mapdl, shaft, Loading(fx=1), dict())

    trial.set_user_attr("rpms", list(rpms))
    trial.set_user_attr("utilization", (f_moment_1, f_moment_2, f_force))
    trial.set_user_attr("rpm", rpm)
    return mass, max(f_moment_1, f_moment_2, f_force), np.abs(rpm - rpm_min), deform


material_selection = [
    # "GFK",
    r"CFK_{230}",
    r"CFK_{395}",
    "HTS40",
]
n_trials = 500

"""
sampler_nsga3 = samplers.NSGAIIISampler()
study = create_study(
    study_name="simulation_nsga3",
    storage="sqlite:///db.sqlite3",
    sampler=sampler_nsga3,
    load_if_exists=True,
    directions=["minimize", "minimize", "maximize", "maximize"],
)
study.optimize(objective, n_trials=n_trials)
"""


sampler_nsga2 = samplers.NSGAIISampler()
study = create_study(
    study_name="simulation_nsga2",
    storage="sqlite:///db.sqlite3",
    sampler=sampler_nsga2,
    load_if_exists=True,
    directions=["minimize", "minimize", "maximize", "maximize"],
)
study.optimize(objective, n_trials=n_trials)

sampler_tpe = samplers.TPESampler()
study = create_study(
    study_name="simulation_tpe",
    storage="sqlite:///db.sqlite3",
    sampler=sampler_tpe,
    load_if_exists=True,
    directions=["minimize", "minimize", "maximize", "maximize"],
)
study.optimize(objective, n_trials=n_trials)

# optuna-dashboard.exe sqlite:///examples/db.sqlite3
