import re
import numpy as np

from ansys.mapdl.core import launch_mapdl

mapdl = launch_mapdl()

# setup the full file
mapdl.prep7()
mapdl.block(0, 1, 0, 1, 0, 1)
mapdl.et(1, 186)
mapdl.esize(0.5)
mapdl.vmesh("all")

# Define a material (nominal steel in SI)
mapdl.mp("EX", 1, 210e9)  # Elastic moduli in Pa (kg/(m*s**2))
mapdl.mp("DENS", 1, 7800)  # Density in kg/m3
mapdl.mp("NUXY", 1, 0.3)  # Poisson's Ratio

# solve first 10 non-trivial modes
out = mapdl.modal_analysis(nmode=10, freqb=1)
print(out)

# store the first 10 natural frequencies
mapdl.post1()
resp = mapdl.set("LIST")
w_n = np.array(re.findall(r"\s\d*\.\d\s", resp), np.float32)
print(w_n)
