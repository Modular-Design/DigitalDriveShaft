from ansys.mapdl.core import launch_mapdl, find_ansys
from src.DigitalDriveShaft.basic import TransverselyIsotropicMaterial, Ply
from src.DigitalDriveShaft.cylindrical import SimpleDriveShaft, Stackup
import math
import numpy as np


composite_HTS40 = TransverselyIsotropicMaterial(E_l=240, E_t=70,
                                                nu_lt=0.28, nu_tt=0.28,
                                                G_lt=2634.2, G_tt=2634.2,
                                                density=1.515,
                                                )  # "HTS40"
composite_HTS40.set_id(1)
# steel = IsotropicMaterial(Em=210, nu=0.21, density = 7.89)

ply0 = Ply(material=composite_HTS40,
           thickness=1)
ply45 = ply0.rotate(45)
stackup = Stackup([ply45, ply0, ply45])

shaft = SimpleDriveShaft(2, 5, stackup)

mapdl = launch_mapdl(mode="grpc")
mapdl.finish()
mapdl.run("/clear")
mapdl.run("/facet,fine")  # feinere Aufteilung der Facetten

mapdl.prep7()
shaft.add_to_mapdl(mapdl, 1)
mapdl.eplot()

