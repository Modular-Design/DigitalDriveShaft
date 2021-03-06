# -*- coding: utf-8 -*-

from src.DigitalDriveShaft.basic import *
from src.DigitalDriveShaft.cylindrical import *
from src.DigitalDriveShaft.analysis import calc_strength


"Parameter Definition"
safety = 1.6  # TODO: safety is not relevant now

"Geometry"
innen_diameter = 171  # mm
shaft_length = 400  # mm

"Loading"
# x in Längsachse der Welle, y, z out of plane
load = Loading(mz=168960, rpm=136000)

"Materialauswahl"

HTS40_max_stress_failure = MaxStressFailure([(-630.93, 850),
                                             (-200, 55),
                                             120])  # MPa

HTS40_cuntze_failure = CuntzeFailure(240, 2200, 1850, 55, -200, 120)  # MPa Values are only placeholder

HTS40_mat = TransverselyIsotropicMaterial(E_l=240, E_t=70,
                                          nu_lt=0.28, nu_tt=0.28,
                                          G_lt=2634.2, G_tt=2634.2,
                                          density=1.515,
                                          failures=[HTS40_max_stress_failure, HTS40_cuntze_failure])  # "HTS40"



# steel = IsotropicMaterial(Em=210, nu=0.21, density = 7.89)

ply0 = Ply(material=HTS40_mat,
           thickness=1)
ply45 = ply0.rotate(45)
stackup = Stackup([ply45, ply0, ply45])

shaft = SimpleDriveShaft(innen_diameter, shaft_length, stackup)

print(f"drive will hold: {calc_strength(shaft, load)}")
