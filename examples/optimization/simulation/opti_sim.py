from data import mapdl, create_shaft, M_max, N_max
from DigitalDriveShaft.analysis import Loading
from DigitalDriveShaft.sim.evaluation import (
    calc_buckling,  # noqa
    calc_eigenfreq,
    calc_strength,
)

from optuna import create_study

from typing import Union, Sequence

# https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer

# launch_mapdl(mode="grpc", loglevel="ERROR")


def objective(trial) -> Union[float, Sequence[float]]:
    n_layers = 4  # trial.suggest_int("n_layers", 1, 6)
    shape = trial.suggest_float("shape", 0.0, 1.0)
    thicknesses = []
    angles = []
    materials = []

    for i in range(n_layers):
        thicknesses.append(trial.suggest_float(f"t{i}", 0.2, 4, step=0.2))
        angles.append(
            trial.suggest_float(f"a{i}", -90.0, 90.0, step=1.0),
        )
        materials.append(
            trial.suggest_categorical(f"material{i}", ["CFK"])  # , "Alu", "GFK"
        )

    shaft = create_shaft(materials, shape, n_layers, thicknesses, angles)
    mass = shaft.get_mass()
    f_moment = calc_strength(mapdl, shaft, Loading(mz=M_max), dict())  # Nm
    f_force = calc_strength(mapdl, shaft, Loading(fz=N_max), dict())  # Nm
    # buck_moment = calc_buckling(mapdl, shaft, None, "MOMENT")[0] * 1000.0  # [Nm]
    rpm = calc_eigenfreq(mapdl, shaft, None)[0] * 60  # [RPM]
    trial.set_user_attr("utilization", (f_moment, f_force))
    return mass, max(f_moment, f_force), rpm


study = create_study(
    study_name="simulation",
    storage="sqlite:///db.sqlite3",
    load_if_exists=True,
    directions=["minimize", "minimize", "maximize"],
)
study.optimize(objective, n_trials=100)

# optuna-dashboard.exe sqlite:///examples/db.sqlite3
