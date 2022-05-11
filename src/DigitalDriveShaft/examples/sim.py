from ansys.mapdl.core import launch_mapdl, find_ansys
from src.DigitalDriveShaft.basic import TransverselyIsotropicMaterial, Ply
from src.DigitalDriveShaft.cylindrical import DriveShaft, \
    Stackup, CylindricalStackup, CylindricalForm, EContour

import numpy as np

"""
https://mapdldocs.pyansys.com/examples/06-verif-manual/vm-006-pinched_cylinder.html?highlight=plot%20shell
"""

"""
CONSTANTS
"""
length = 1000  # 10  # 1000  # mm
r_inner = 30.0  # 5  # 30 # mm
z_div = 15.0  # 30
phi_div = 16.0  # 10
mesh_type = "SOLID"  # choose between SOLID or SHELL

dz = length / z_div
phi_max = np.pi
phi_min = -np.pi
dphi = (phi_max - phi_min) / phi_div

"""
Form Definitions
"""
form_id = "crazy"
form_func = {"normal": lambda z, phi: r_inner,
             "cone": lambda z, phi: r_inner * (3.0 - 2.0 * z / length),
             "invers": lambda z, phi: r_inner * (3.0 - 2.0 * np.cos(z / (4.0 * length) * 2 * np.pi)),
             "optimal": lambda z, phi: r_inner * (3.0 - 2.0 * (z / (length)) ** 2),
             "crazy": lambda z, phi: r_inner * (3.0 - 2.0 * (z / (length)) ** 2) *
                                     (1.0 + 0.5 * np.cos(z / (1.0 * length) * 5 * np.pi))}

form = CylindricalForm(form_func[form_id], length)

"""
Layer Definitions
"""

# composite = TransverselyIsotropicMaterial(E_l=240e6, E_t=70e6,
#                                           nu_lt=0.28, nu_tt=0.28,
#                                           G_lt=2634.2, G_tt=2634.2,
#                                           density=1.515,
#                                           )  # "HTS40"

composite = TransverselyIsotropicMaterial(E_l=1.21e5, E_t=8600,  # MPa bzw. N / mm^2
                                          nu_lt=0.27, nu_tt=0.4,
                                          G_lt=4700, G_tt=3100,
                                          density=1.49e-6,  # kg / mm^2
                                          )  # "230GPa Prepreg"

composite.set_id(1)

# steel = IsotropicMaterial(Em=210, nu=0.21, density = 7.89)

ply0 = Ply(material=composite,
           thickness=0.5)
ply45 = ply0.rotate(np.pi / 4)  # 45°
ply90 = ply0.rotate(np.pi / 2)  # 90°

layer = Stackup([ply90, ply45, ply0, ply45, ply90])  # ply45, ply45


# layer = Stackup([ply0])


def stackup_func(z, phi):
    return layer


stackup = CylindricalStackup(stackup_func)
shaft = DriveShaft(form, stackup, EContour.INNER)

"""
ANSYS SIMULATION
"""

mapdl = launch_mapdl(mode="grpc", loglevel="ERROR")  # "INFO", "ERROR"  log_apdl='sim_log.txt'
mapdl.finish()
mapdl.clear()
mapdl.verify()

mapdl.run("/facet,fine")  # feinere Aufteilung der Facetten

mapdl.prep7()

composite.add_to_mapdl(mapdl)
shaft.add_to_mapdl(mapdl, dz=dz, phi_max=phi_max, phi_min=phi_min, dphi=dphi, type=mesh_type)
mapdl.asel("ALL")
# mapdl.nplot(vtk=True, nnum=True, background="", cpos="iso", show_bounds=True, point_size=10)
# mapdl.vplot(show_bounds=True)
# mapdl.eplot(show_bounds=True, show_node_numbering=True)

mapdl.nummrg("NODE")
"""
q = mapdl.queries
zs = np.arange(0, length + dz, dz)
rotpairs = np.zeros((len(zs), 2), dtype=int)
name = "ROTPAIRS"
mapdl.run(f"*DIM,{name}, ARRAY, 2, {len(zs)}")
for i in range(len(zs)):
    z = zs[i]
    r = shape_func(z, phi_min)
    low_node = q.node(r, phi_min / np.pi * 180, z)
    r = shape_func(z, phi_max)
    high_node = q.node(r, phi_max / np.pi * 180, z)
    mapdl.run(f"*set, {name}(1, {i + 1}), {low_node}, {high_node}")

# mapdl.parameters["ROTPAIRS"] = rotpairs
mapdl.cyclic(2 * np.pi / (phi_max-phi_min), "", 1, "", "", name)
mapdl.cycopt("LDSECT", 1)
"""


def plot_nodal_disp():
    # Define global cartesian coordinate system.
    # mapdl.csys(0)
    mapdl.post1()
    mapdl.set(1)
    # mapdl.post_processing.plot_nodal_displacement(
    #     title="Nodal Displacements",
    #     component="Z",
    #     cpos="zx",
    #     scalar_bar_args={"title": "Nodal Displacements", "vertical": True},
    #     # show_node_numbering=True,
    #     show_axes=True,
    #     show_edges=True,
    # )

    mapdl.post_processing.plot_nodal_displacement(
        title="", # Nodal Displacements
        component="Z",
        cpos="zx",
        scalar_bar_args={"vertical": True},
        # scalar_bar_args={"title": "Nodal Displacements", "vertical": True},
        # show_node_numbering=True,
        show_axes=True,
        # show_edges=True,
        savefig=f"{form_id}_driveshaft.png",
        window_size=[1024, 512],
        # off_screen=True
    )


def plot_nodal_stress():
    # Define global cartesian coordinate system.
    # mapdl.csys(0)
    mapdl.post1()
    mapdl.set(1)
    # mapdl.post_processing.plot_nodal_eqv_stress()
    mapdl.post_processing.plot_nodal_principal_stress('1', savefig=f"{form_id}_driveshaft.png",
                                                      cpos='iso', window_size=[1024, 512],
                                                      off_screen=True)
    # mapdl.post_processing.plot_nodal_principal_stress('2')


def fixation():
    if mesh_type == "SHELL":
        mapdl.nsel("S", "LOC", "Z", form.min_z())
        # mapdl.d("ALL", "UZ", 0)
        # mapdl.nsel("R", "LOC", "Y", 0)
        mapdl.d("ALL", "UX", 0)
        mapdl.d("ALL", "UY", 0)
        mapdl.d("ALL", "UZ", 0)
    else:
        # mapdl.nsel("S", "LOC", "X", shaft.get_inner_radius(0, 0))
        # mapdl.d("ALL", "UX", 0)
        # mapdl.d("ALL", "UY", 0)
        mapdl.nsel("S", "LOC", "Z", form.min_z())
        # mapdl.d("ALL", "UZ", 0)
        mapdl.d("ALL", "UX", 0)
        mapdl.d("ALL", "UY", 0)
        mapdl.d("ALL", "UZ", 0)
    """
    mapdl.nsel("S", "LOC", "Z", form.min_z())
    mapdl.d("ALL", "UZ", 0)
    mapdl.d("ALL", "UY", 0)
    mapdl.d("ALL", "UZ", 0)
    mapdl.run("ALLS")
    """


def axial_loading():
    mapdl.run("/solu")
    # Displacements
    fixation()
    max_z = form.max_z()

    if mesh_type == "SHELL":
        radius = shaft.get_center_radius(max_z, 0, False)
        mapdl.lsel("S", "LOC", "Z", max_z)
        # mapdl.f("ALL", "FZ", 1)
        mapdl.sfl("ALL", "PRES", - 1 / (2 * np.pi * radius))
    else:
        inner_radius = shaft.get_inner_radius(max_z, 0, False)
        outer_radius = shaft.get_outer_radius(max_z, 0, False)
        mapdl.asel("S", "LOC", "Z", form.max_z())
        mapdl.sfa("ALL", "", "PRES", -1 / (np.pi * (outer_radius ** 2 - inner_radius ** 2)))
    # very important!!
    # leaving this out can result in wrong results in 50% of the cases
    mapdl.allsel()

    mapdl.antype("STATIC")
    mapdl.outres("ALL", "ALL")
    mapdl.solve()
    mapdl.finish()

    mapdl.post1()

    result = mapdl.result
    nodenump, stress = result.principal_nodal_stress(0)

    s1max = np.nanmax(stress[:, -5])
    s2max = np.nanmax(stress[:, -4])

    s1list = stress[:, -5].tolist()
    s2list = stress[:, -4].tolist()
    p1max = mapdl.mesh.nodes[s1list.index(s1max)]
    p2max = mapdl.mesh.nodes[s2list.index(s2max)]
    plot_nodal_disp()
    # plot_nodal_stress()
    return p1max, p2max


print(axial_loading())

quit()


def modal_analysis():
    # Modual-Analysis
    mapdl.run("/SOLU")
    mapdl.omega("", "", "1")
    fixation()
    mapdl.outres("ALL", "ALL")

    mapdl.antype("MODAL")
    mapdl.modopt("lanb", 3)
    mapdl.mxpand("", "", "", "yes")

    mapdl.solve()
    mapdl.finish()

    mapdl.post1()

    result = mapdl.result
    result.animate_nodal_solution(0)
    f = result.time_values
    return f


# print(modal_analysis())


mapdl.exit()
