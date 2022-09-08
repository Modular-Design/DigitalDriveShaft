from src.DigitalDriveShaft.basic import TransverselyIsotropicMaterial, Ply, Stackup, Loading, CuntzeFailure
from src.DigitalDriveShaft.cylindrical import SimpleDriveShaft
from src.DigitalDriveShaft.sim.cylindrical import driveshaft_to_mapdl, CylindricMeshBuilder
import pytest
from ansys.mapdl.core import launch_mapdl
import numpy as np

hts40_cuntze = CuntzeFailure(
    E1=145200,  # MPa
    R_1t=852.0, R_1c=631,  # MPa
    R_2t=57, R_2c=274, R_21=132  # MPa
)
hts40_mat = TransverselyIsotropicMaterial(E_l=145200,  # MPa
                                          E_t=6272.7,  # MPa
                                          nu_lt=0.28,  # MPa
                                          G_lt=2634.2,  # MPa
                                          density=1.58,  # g/cm^3
                                          failures=[hts40_cuntze])  # MPa


def generate_stackup(mat, layer_thickness, deg_orientations):
    plies = []
    for orientation in deg_orientations:
        plies.append(Ply(mat, layer_thickness, orientation, degree=True))

    return Stackup(plies)


mapdl = launch_mapdl(mode="grpc", loglevel="Error")


@pytest.mark.parametrize(
    "l_thickness, l_orientations, ds_diameter, ds_length",
    [
        (1.0, [0], 10, 10),  # fz in N
        # (1.0, [90], 10, 10),  # fz in N
    ]
)
def test_driveshaft(l_thickness, l_orientations, ds_diameter, ds_length):
    stackup = generate_stackup(hts40_mat, l_thickness, l_orientations)
    shaft = SimpleDriveShaft(diameter=ds_diameter, length=ds_length, stackup=stackup)
    mapdl.finish()
    mapdl.clear()
    mapdl.prep7()
    driveshaft_to_mapdl(mapdl, shaft, "SHELL", dict(n_z=1, n_phi=1, phi_max=np.pi / 2))
    # mapdl.eplot()
    print("### mplist ###")
    print(mapdl.mplist(1, lab="DENS"))
    print("### tblist ###")
    print(mapdl.tblist())
    assert True
