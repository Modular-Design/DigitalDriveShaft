from ansys.mapdl.core import launch_mapdl, find_ansys
from src.DigitalDriveShaft.basic import TransverselyIsotropicMaterial, Ply
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
r_inner = 30  # mm


"""
Form Definitions
"""


def shape_func(z, phi):
    return r_inner * np.sin(z / length * np.pi) + r_inner


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

# stackup = Stackup([ply45, ply0, ply45])
layer = Stackup([ply0])


def stackup_func(z, phi):
    return layer


stackup = CylindricalStackup(stackup_func)

shaft = DriveShaft(form, stackup)


"""
ANSYS SIMULATION
"""

mapdl = launch_mapdl(mode="grpc", loglevel="ERROR", log_apdl='shell_log.txt')  # "INFO", "ERROR"
mapdl.finish()
mapdl.clear()
mapdl.verify()

mapdl.run("/facet,fine")  # feinere Aufteilung der Facetten

mapdl.prep7()

composite_HTS40.add_to_mapdl(mapdl)
shaft.add_to_mapdl(mapdl)
mapdl.eplot(show_bounds=True, show_node_numbering=True)

mapdl.nummrg("NODE")

# Displacements
mapdl.nsel("S", "LOC", "Z", form.min_z())
mapdl.d("ALL", "UZ", 0)
mapdl.nsel("R", "LOC", "Y", 0)
mapdl.d("ALL", "ALL", 0)

# Loading
# nodes = mapdl.nsel("S", "LOC", "Z", form.max_z())
# print(nodes)
# n_nodes = int(re.findall(r"(\d+)\s+NODES", nodes)[0])
# mapdl.f("ALL", "FZ", 1 / n_nodes)

mapdl.lsel("S", "LOC", "Z", form.max_z())
mapdl.sfl("ALL", "PRES", 1)

# very important!!
# leaving this out can result in wrong results in 50% of the cases
mapdl.allsel()


def solve_procedure():
    mapdl.run("/solu")
    mapdl.antype("STATIC")
    out = mapdl.solve()
    mapdl.finish()
    return out


solve_procedure()


# Start post-processing mode.
def post_processing():
    mapdl.post1()
    mapdl.set(1)


post_processing()


def plot_nodal_disp():
    mapdl.post_processing.plot_nodal_displacement(
        title="Nodal Displacements",
        component="NORM",
        cpos="zx",
        scalar_bar_args={"title": "Nodal Displacements", "vertical": True},
        show_node_numbering=True,
        show_axes=True,
        show_edges=True,
    )


plot_nodal_disp()


mapdl.exit()

