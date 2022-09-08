from optuna import create_study
from src.DigitalDriveShaft.basic import TransverselyIsotropicMaterial, Ply, Stackup, Loading, CuntzeFailure
from src.DigitalDriveShaft.cylindrical import DriveShaft, CylindricalStackup, CylindricalForm
from src.DigitalDriveShaft.sim.evaluation import calc_buckling, calc_eigenfreq, calc_strength
from ansys.mapdl.core import launch_mapdl
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
                                          density=1.58,  # g/cm^3 -> 1e-6 kg/mm^3
                                          failures=[hts40_cuntze])  # MPa


material_legend = {
    "CFK": hts40_mat,
    "Alu": None,
    "GFK": None,
}

mapdl = launch_mapdl(mode="grpc", loglevel="ERROR")


def objective(trial) -> Union[float, Sequence[float]]:
    n_layers = trial.suggest_int("n_layers", 1, 6)
    thicknesses = []
    angles = []
    materials = []

    for i in range(n_layers):
        thicknesses.append(trial.suggest_float(f't{i}', 0.2, 4, step=0.2))
        angles.append((
            trial.suggest_float(f'a{i}', -90.0, 90.0, step=1.0),
            trial.suggest_float(f'b{i}', -90.0, 90.0, step=1.0)
        ))
        materials.append(trial.suggest_categorical(f'material{i}', ["CFK"]))  # , "Alu", "GFK"

    cyl_form = CylindricalForm(lambda z, phi: 10, 500)  # 10 mm inner radius

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
    cuntze = calc_strength(mapdl, shaft, Loading(mz=1e3), dict())  # Nm
    buck_moment = calc_buckling(mapdl, shaft, None, "MOMENT")[0] * 1000.0  # [Nm]
    rpm = calc_eigenfreq(mapdl, shaft, None)[0] * 60  # [RPM]
    # if buckling < 1.0:
    #     raise TrialPruned
    return mass, cuntze, buck_moment, rpm


study = create_study(
    study_name="simulation",
    storage="sqlite:///db.sqlite3",
    load_if_exists=True,
    directions=["minimize", "minimize", "maximize", "maximize"])
study.optimize(objective, n_trials=100)

# optuna-dashboard.exe sqlite:///examples/db.sqlite3
