import numpy as np
from ansys.mapdl.core import launch_mapdl

# Start mapdl.
mapdl = launch_mapdl()


def start_prep7():
    mapdl.clear()
    mapdl.verify()
    mapdl.prep7()


start_prep7()


# Define the element type number.
def define_element(elem_type):
    # Type of analysis: Static.
    mapdl.antype("STATIC")
    # Define the element type number.
    elem_num = 1
    if elem_type == "SHELL181":
        # Element type: SHELL181.
        mapdl.et(elem_num, elem_type)
        mapdl.keyopt(elem_num, 3, 2)  # Cubic shape function

    elif elem_type == "SHELL281":
        # Element type: SHELL181.
        mapdl.et(elem_num, "SHELL281")

    return elem_type, mapdl.etlist()


# Return the number of the element type.
elem_type, elem_type_list = define_element(elem_type="SHELL181")
print(
    f"Selected element type is: {elem_type},\n"
    f"Printout the element list with its own properties:\n {elem_type_list}"
)


# Define material number.
mat_num = 1
radius = 4
length = 5
ndiv = 8


# Define material properties.
def define_material():
    # Define material properties.
    mapdl.mp("EX", mat_num, 10.5e6)
    mapdl.mp("NUXY", mat_num, 0.3125)
    return mapdl.mplist()


material_list = define_material()
print(material_list)

# Define cross-section number and thickness of the shell element.
sec_num = 1
t = 0.094


# Define shell cross-section.
def define_section():
    # Define shell cross-section.
    mapdl.sectype(secid=sec_num, type_="SHELL", name="shell181")
    mapdl.secdata(t, mat_num, 0, 5)
    return mapdl.slist()


section_list = define_section()
print(section_list)


# Define geometry of the simplified mathematical model.
def define_geometry():
    # Change active coordinate system
    # to the global cylindrical coordinate system.
    mapdl.csys(1)
    # Define keypoints by coordinates.
    dz = length / (ndiv)
    zs = np.arange(0, length + dz, dz)
    dphi = 90 / (ndiv)
    phis = np.arange(0, 90 + dphi, dphi)

    i = 1
    for z in zs:
        for phi in phis:
            mapdl.k(i, radius, phi, z)
            i += 1

    for j in range(ndiv):
        for i in range(ndiv):
            a = (j) * len(zs) + i + 1
            b = (j) * len(zs) + i + 2
            c = (j+1) * len(zs) + i + 2
            d = (j+1) * len(zs) + i + 1
            mapdl.a(a, d, c, b)
            # mapdl.aplot(show_bounds=True)


define_geometry()


# Define mesh properties and create the mesh with shell elements.
def meshing():
    # Specify the default number of line divisions.
    # mapdl.esize(size="", ndiv=1)
    for i in range(ndiv * ndiv):
        mapdl.asel("S", "AREA", '', i + 1)
        mapdl.esize(0, 1)
        mapdl.amesh("ALL")

meshing()

mapdl.eplot(vtk=True, show_node_numbering=True)
# mapdl.del("ALL")


# Select nodes by location and apply BC.
def define_bc():
    # Select nodes by location and apply BC.
    mapdl.nsel("S", "LOC", "Z", 0)
    mapdl.d("ALL", "UZ", 0)
    mapdl.nsel("R", "LOC", "Y", 0)
    mapdl.d("ALL", "ALL", 0)
    mapdl.nsel("ALL")


define_bc()


# Define loads.
def define_loads():
    mapdl.lsel("S", "LOC", "Z", length)
    mapdl.sfl("ALL", "PRES", 1)
    mapdl.allsel()


define_loads()


def solve_procedure():
    mapdl.run("/solu")
    out = mapdl.solve()
    mapdl.finish()
    return out


simulation_info = solve_procedure()
print(simulation_info)


# Start post-processing mode.
def post_processing():
    mapdl.post1()
    mapdl.set(1)


post_processing()


def plot_nodal_disp():
    mapdl.post_processing.plot_nodal_displacement(
        title="Nodal Displacements",
        component="Z",
        cpos="zx",
        scalar_bar_args={"title": "Nodal Displacements", "vertical": True},
        show_node_numbering=True,
        show_axes=True,
        show_edges=True,
    )


plot_nodal_disp()
# [0, -5.07e-6]
