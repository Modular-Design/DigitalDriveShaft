from ansys.mapdl.core import launch_mapdl

mapdl = launch_mapdl(log_apdl='pymapdl_log.txt')
mapdl.finish()
mapdl.run("/clear")
mapdl.prep7()

mapdl.et(1, "SHELL181")
mapdl.mp("EX", 1, 2e5)
mapdl.mp("PRXY", 1, 0.3)

mapdl.et(2, "SHELL181")  # weaker layer
mapdl.mp("EX", 1, 1e5)
mapdl.mp("PRXY", 1, 0.3)

mapdl.rectng(0, 1, 0, 1)
mapdl.sectype(1, "SHELL")
mapdl.secdata(0.1, 1)
mapdl.secdata(0.2, 1)
mapdl.secdata(0.1, 1)
mapdl.esize(0.2)
mapdl.amesh("all")

mapdl.eshape(1)
mapdl.eplot()