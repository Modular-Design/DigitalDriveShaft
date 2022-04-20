from src.DigitalDriveShaft.basic import TransverselyIsotropicMaterial, \
    Ply, Stackup, Loading
from src.DigitalDriveShaft.cylindrical import SimpleDriveShaft
from src.DigitalDriveShaft.analysis import calc_strength
import numpy as np


HTS40_Epoxy = TransverselyIsotropicMaterial(E_l=145200,  # MPa
                                            E_t=6272.7,  # MPa
                                            nu_lt=0.28,  # MPa
                                            G_lt=2634.2,  # MPa
                                            density=1.58,  # g/cm^3
                                            R_1t=852.0,   #MPa
                                            R_1c=630.93) #MPa

ply_0 = Ply(material=HTS40_Epoxy,
           thickness=10.1/4)

ply_45 = ply_0.rotate(np.pi/4)  # 45°
ply_n45 = ply_0.rotate(-np.pi/4)  # -45°

# ply90 = ply0.rotate(np.pi/2)  # 90°

stackup = Stackup([ply_45, ply_n45, ply_45, ply_45])

shaft = SimpleDriveShaft(85.5*2, 100, stackup)

loading = Loading(mz=168960)  # Nm

print(calc_strength(shaft, loading))

