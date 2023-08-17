import optuna
from pathlib import Path
from DigitalDriveShaft.analysis import Loading

from data import create_shaft, mapdl, M_max
from DigitalDriveShaft.sim.evaluation import (
    # calc_buckling,  # noqa
    # calc_eigenfreq,
    calc_strength,
    # calc_bending,
)


trail_id = 969
n_layers = 4

study = optuna.create_study(
    study_name="simulation",  # simulation_metal or simulation_composite
    storage="sqlite:////home/willi/Nextcloud/share/sim6/db.sqlite3",
    load_if_exists=True,
)

df = study.trials_dataframe(
    attrs=("number", "value", "params", "user_attrs", "duration", "state")
)

result_path = (Path(__file__).parent / "data").absolute()

trail = df.loc[[trail_id]]

print(trail)

materials = [trail[f"params_material{i}"].values[0] for i in range(n_layers)]
ts = [trail[f"params_t{i}"].values[0] for i in range(n_layers)]
angles = [trail[f"params_a{i}"].values[0] for i in range(n_layers)]
shape = trail["params_shape"].values[0]
print(shape)

n_layers = 4
angles[0], angles[1], angles[2], angles[3] = -45, 45, -45, 45
ts[0], ts[1], ts[2], ts[3] = 3, 3, 3, 3


for i in range(n_layers):
    print(f"{i}: {materials[i]}, {ts[i]}mm, {angles[i]}°")

shaft = create_shaft(materials, shape, n_layers, ts, angles)
if True:
    mapdl.open_apdl_log(result_path / f"shaft_{trail_id}.inp")
    f_moment = calc_strength(mapdl, shaft, Loading(mz=M_max), dict(n_phi=32, n_z=20))
    print(f_moment)

mapdl.rsys("LSYS")
for i in range(n_layers):
    mapdl.nsel("S", "LOC", "Z", 0, shaft.get_length() * 0.8)
    # mapdl.nsel("ALL")
    mapdl.layer(i + 1)
    mapdl.shell("bot")
    mapdl.post_processing.plot_element_stress(
        "X", window_size=[1920, 1080], savefig=result_path / f"stress_eX_{i+1}_bot.png"
    )
    mapdl.post_processing.plot_element_stress(
        "Y", window_size=[1920, 1080], savefig=result_path / f"stress_eY_{i+1}_top.png"
    )
    mapdl.shell("top")
    mapdl.post_processing.plot_element_stress(
        "X", window_size=[1920, 1080], savefig=result_path / f"stress_eX_{i+1}_top.png"
    )
    mapdl.post_processing.plot_element_stress(
        "Y", window_size=[1920, 1080], savefig=result_path / f"stress_eY_{i+1}_bot.png"
    )
# grid = mapdl.mesh.grid
# grid.save(result_path/ f"shaft_{trail_id}.vtk" )
