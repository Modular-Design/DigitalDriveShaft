from src.DigitalDriveShaft.basic import TransverselyIsotropicMaterial, Ply, Stackup, Loading, CuntzeFailure
from src.DigitalDriveShaft.cylindrical import SimpleDriveShaft
from src.DigitalDriveShaft.analysis import calc_crit_moment
from src.DigitalDriveShaft.sim.evaluation import calc_buckling
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
    "l_thickness, l_orientations, ds_diameter, ds_length, fkrit",
    [
        (1.0, [0], 10, 30, 0.376),   # fkrit in N
        (1.0, [90], 10, 30, 0.144),   # fkrit in N
    ]
)
def test_buckle_force(l_thickness,  l_orientations, ds_diameter, ds_length, fkrit):
    stackup = generate_stackup(hts40_mat, l_thickness, l_orientations)
    shaft = SimpleDriveShaft(diameter=ds_diameter, length=ds_length, stackup=stackup)
    result = calc_buckling(mapdl, shaft, dict(), "FORCE")
    assert abs(result[0] - fkrit) < 0.01


@pytest.mark.parametrize(
    "l_thickness, l_orientations, ds_diameter, ds_length",
    [
        (1.0, [90], 10, 30),
        (15.58/4, [45, -45, -45, 45], 79.42*2, 400),
        (11.02/7, [45, -45, 90, 0, 90, -45, 45], 79.42*2, 400),
    ]
)
def test_analytic_vs_sim(l_thickness, l_orientations, ds_diameter, ds_length):
    stackup = generate_stackup(hts40_mat, l_thickness, l_orientations)
    shaft = SimpleDriveShaft(diameter=ds_diameter, length=ds_length, stackup=stackup)
    sim = calc_buckling(mapdl, shaft, dict(), "MOMENT") * 1000  # [Nm]
    analytic = calc_crit_moment(shaft)
    assert abs(sim[0] - analytic) < 0.01
