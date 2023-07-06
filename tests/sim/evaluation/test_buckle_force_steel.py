from src.DigitalDriveShaft.basic import IsotropicMaterial, Ply, Stackup
from src.DigitalDriveShaft.cylindrical import SimpleDriveShaft, EContour
from src.DigitalDriveShaft.sim.evaluation import calc_buckling
import pytest
from ansys.mapdl.core import launch_mapdl


steel = IsotropicMaterial(200000, 0.3, 7.85e-09)  # [t s^-2 mm^-1]  # []  # [t mm^-3]


def generate_stackup(mat, layer_thickness, deg_orientations):
    plies = []
    for orientation in deg_orientations:
        plies.append(Ply(mat, layer_thickness, orientation, degree=True))

    return Stackup(plies)


mapdl = launch_mapdl(
    mode="grpc",
    # loglevel="DEBUG",
    loglevel="ERROR",
)


@pytest.mark.parametrize(
    "l_thickness, ds_diameter, ds_length, fkrit",
    [
        (1.0, 10, 300, 67954),  # fkrit in N
        # (1.0, 10, 30, 0.144),   # fkrit in N
    ],
)
def test_buckle_force(l_thickness, ds_diameter, ds_length, fkrit):
    stackup = generate_stackup(steel, l_thickness, [0])
    shaft = SimpleDriveShaft(
        diameter=ds_diameter, length=ds_length, stackup=stackup, contour=EContour.CENTER
    )
    result = calc_buckling(
        mapdl, shaft, dict(n_phi=20, n_z=50), "FORCE"
    )  # dict(n_phi=20, n_z=50)
    assert abs(result - fkrit) / fkrit < 0.05
