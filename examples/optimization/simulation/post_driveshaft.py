from data import mapdl, create_shaft, M_max, N_max  # noqa
from post_plots import best_candidate as bconf
from DigitalDriveShaft.analysis import Loading
from DigitalDriveShaft.sim.evaluation import (
    calc_buckling,  # noqa
    calc_eigenfreq,  # noqa
    calc_strength,  # noqa
)  # noqa


thicknesses = 12
materials = []
angles = []
for i in range(4):
    materials.append(bconf.iloc[0][f"params_material{i}"])
    angles.append(bconf.iloc[0][f"params_a{i}"])

shape = -0.99  # bconf.iloc[0]["params_shape"]
n_layers = len(materials)
print(angles)

shaft = create_shaft(materials, shape, n_layers, thicknesses, angles)
# f_moment = calc_strength(mapdl, shaft, Loading(mz=M_max), dict())

cpos = [
    (558.8225704852507, 1016.450672259557, -472.1599271809821),
    (14.789884499441456, 32.023932983373086, 301.17012630856846),
    (0.9171367736370943, -0.31275315443066026, 0.24707408370003783),
]
# mapdl.eplot(
#     vtk=True, smooth_shading=True,
#     # plot_bc=True, bc_labels=["UX", "UZ"], plot_bc_labels=True,
#     # background='w',
#     cpos=cpos,
#     window_size=[1920, 1080], savefig='shape.png',off_screen=True
# )


f_force = calc_strength(mapdl, shaft, Loading(fz=N_max), dict())  # Nm
mapdl.post_processing.plot_nodal_displacement(
    component="Z",
    smooth_shading=True,
    cpos=cpos,
    window_size=[1920, 1080],
    savefig="axial_displacement.png",
    off_screen=True,
)


# f_moment = calc_strength(mapdl, shaft, Loading(mz=M_max), dict())  # Nm
# mapdl.
# f_force = calc_strength(mapdl, shaft, Loading(fz=N_max), dict())  # Nm
# # buck_moment = calc_buckling(mapdl, shaft, None, "MOMENT")[0] * 1000.0  # [Nm]
# rpm = calc_eigenfreq(mapdl, shaft, None)[0] * 60  # [RPM]
