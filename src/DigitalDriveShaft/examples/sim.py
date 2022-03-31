from ansys.mapdl.core import launch_mapdl, find_ansys
from src.DigitalDriveShaft.basic import TransverselyIsotropicMaterial, Ply, IsotropicMaterial
from src.DigitalDriveShaft.cylindrical import DriveShaft, Stackup, CylindricalStackup, CylindricalForm
import re
import math
import numpy as np

"""
https://mapdldocs.pyansys.com/examples/06-verif-manual/vm-006-pinched_cylinder.html?highlight=plot%20shell
"""

"""
CONSTANTS
"""
length = 100  # mm
r_inner = 10  # 30 # mm
z_div = 20.0  # 30
phi_div = 10.0  # 10
mesh_type = "SOLID" # choose between SOLID or SHELL


"""
Form Definitions
"""


def shape_func(z, phi):
    return r_inner + r_inner * 0.5 * np.sin(z * 1.0 / (4.0 * length) * 2 * np.pi)


form = CylindricalForm(shape_func, length)


"""
Layer Definitions
"""

composite_HTS40 = TransverselyIsotropicMaterial(E_l=240e6, E_t=70e6,
                                                nu_lt=0.28, nu_tt=0.28,
                                                G_lt=2634.2, G_tt=2634.2,
                                                density=1.515,
                                                )  # "HTS40"
composite_HTS40.set_id(1)

# steel = IsotropicMaterial(Em=210, nu=0.21, density = 7.89)

ply0 = Ply(material=composite_HTS40,
           thickness=1)
ply45 = ply0.rotate(np.pi/4)  # 45°

layer = Stackup([ply45, ply0, ply45])
# layer = Stackup([ply0])


def stackup_func(z, phi):
    return layer


stackup = CylindricalStackup(stackup_func)

shaft = DriveShaft(form, stackup)


"""
ANSYS SIMULATION
"""

mapdl = launch_mapdl(mode="grpc", loglevel="ERROR")  # "INFO", "ERROR"  log_apdl='sim_log.txt'
mapdl.finish()
mapdl.clear()
mapdl.verify()

mapdl.run("/facet,fine")  # feinere Aufteilung der Facetten

mapdl.prep7()

composite_HTS40.add_to_mapdl(mapdl)
dz = length/z_div
phi_max = np.pi/2
phi_min = 0
dphi = (phi_max - phi_min)/(phi_div)
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
    mapdl.post_processing.plot_nodal_displacement(
        title="Nodal Displacements",
        component="Z",
        cpos="zx",
        scalar_bar_args={"title": "Nodal Displacements", "vertical": True},
        # show_node_numbering=True,
        show_axes=True,
        show_edges=True,
    )





def axial_loading():
    mapdl.run("/solu")
    # Displacements

    if mesh_type == "SHELL":
        mapdl.nsel("S", "LOC", "Z", form.min_z())
        mapdl.d("ALL", "UZ", 0)
        mapdl.nsel("R", "LOC", "Y", 0)
        mapdl.d("ALL", "ALL", 0)
        mapdl.lsel("S", "LOC", "Z", form.max_z())
        mapdl.sfl("ALL", "PRES", -1)
    else:
        mapdl.nsel("S", "LOC", "X", shaft.get_inner_radius(0, 0))
        mapdl.d("ALL", "UX", 0)
        mapdl.d("ALL", "UY", 0)
        mapdl.nsel("R", "LOC", "Z", form.min_z())
        mapdl.d("ALL", "UZ", 0)

        mapdl.asel("S", "LOC", "Z", form.max_z())
        # mapdl.aplot(show_bounds=True)
        mapdl.sfa("ALL", "", "PRES", -1)
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
    return p1max, p2max


print(axial_loading())


def modal_analysis():
    # Modual-Analysis
    mapdl.run("/SOLU")
    mapdl.omega("", "", 1)
    mapdl.nsel("S", "LOC", "Z", form.min_z())
    mapdl.d("ALL", "UZ", 0)
    mapdl.d("ALL", "UY", 0)
    mapdl.d("ALL", "UZ", 0)
    mapdl.run("ALLS")
    mapdl.outres("ALL", "ALL")

    mapdl.antype("MODAL")
    mapdl.modopt("lanb", 3)
    mapdl.mxpand("", "", "", "yes")

    mapdl.solve()
    mapdl.finish()

    mapdl.post1()

    result = mapdl.result
    f = result.time_values
    return f


print(modal_analysis())


mapdl.exit()

