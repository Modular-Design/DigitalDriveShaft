from src.DigitalDriveShaft.basic import TransverselyIsotropicMaterial, Ply, Stackup, Loading, CuntzeFailure
from src.DigitalDriveShaft.cylindrical import SimpleDriveShaft
from src.DigitalDriveShaft.sim.evaluation import calc_strength
import pytest
from ansys.mapdl.core import launch_mapdl


hts40_cuntze = CuntzeFailure(
                                E1=145200,  # MPa
                                R_1t=852.0, R_1c=631,  # MPa
                                R_2t=57, R_2c=274, R_21=132     # MPa
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


mapdl = launch_mapdl(mode="grpc", loglevel="ERROR")


@pytest.mark.parametrize(
    "l_thickness, l_orientations, ds_diameter, ds_length, loading, safety",
    [
        (1.0, [0], 10, 30, Loading(fz=100),  285.93),   # fz in N
        (1.0, [90], 10, 30, Loading(fz=100),  19.44),   # fz in N
        (1.0, [0], 10, 30, Loading(fz=1000),  28.593),
    ]
)
def test_axial_laoding(l_thickness,  l_orientations, ds_diameter, ds_length, loading, safety):
    stackup = generate_stackup(hts40_mat, l_thickness, l_orientations)
    shaft = SimpleDriveShaft(diameter=ds_diameter, length=ds_length, stackup=stackup)
    result = calc_strength(mapdl, shaft, loading, dict())
    assert abs(result - safety) < 0.1
