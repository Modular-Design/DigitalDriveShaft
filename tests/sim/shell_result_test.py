from ansys.mapdl.core import launch_mapdl
import re

mapdl = launch_mapdl(log_apdl='pymapdl_log.txt')
mapdl.finish()
mapdl.clear()
mapdl.verify()
# mapdl.run("/facet,fine")

mapdl.prep7()
mapdl.mp("EX", 1, 240e6)
mapdl.mp("EY", 1, 70e6)
mapdl.mp("EZ", 1, 70e6)
mapdl.mp("PRXY", 1, 0.28)
mapdl.mp("PRXZ", 1, 0.28)
mapdl.mp("PRYZ", 1, 0.28)
mapdl.mp("GXY", 1, 2634.2)
mapdl.mp("GXZ", 1, 2634.2)
mapdl.mp("GYZ", 1, 2634.2)
mapdl.mp("DENS", 1, 1.515)
mapdl.csys(1)

for i in range(11):
    mapdl.k(i + 1, 2.5, 0, i)

for i in range(11):
    mapdl.k(i + 12, 2.5, 90, i)

for i in range(10):
    mapdl.a(i + 1, i + 12, i + 13, i + 2)

mapdl.et(1, "SHELL181")
mapdl.keyopt(1, 8, 1)
mapdl.sectype(1, "SHELL")
mapdl.secdata(1, 1, 0, 3)
mapdl.secoffset("BOT")
mapdl.esize(0, 1)
mapdl.type(1)
mapdl.amesh("ALL")

mapdl.nsel("S", "LOC", "Z", 0)
mapdl.d("ALL", "UZ", 0)
mapdl.nsel("R", "LOC", "Y", 0)
mapdl.d("ALL", "ALL", 0)

nodes = mapdl.nsel("S", "LOC", "Z", 10)
mapdl.f("ALL", "FZ", 0.5)
mapdl.allsel()

mapdl.run("/solu")
mapdl.antype("STATIC")
mapdl.solve()
mapdl.finish()

mapdl.post1()
mapdl.set(1)
mapdl.post_processing.plot_nodal_displacement(
        title="Nodal Displacements",
        component="Z",
        cpos="zx",
        scalar_bar_args={"title": "Nodal Displacements", "vertical": True},
        show_node_numbering=True,
        show_axes=True,
        show_edges=True,
    )
mapdl.exit()