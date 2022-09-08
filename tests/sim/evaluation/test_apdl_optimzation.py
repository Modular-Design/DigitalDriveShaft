from src.DigitalDriveShaft.basic import TransverselyIsotropicMaterial, Ply, Stackup, Loading, CuntzeFailure
from src.DigitalDriveShaft.cylindrical import SimpleDriveShaft
from src.DigitalDriveShaft.analysis import calc_crit_moment
from src.DigitalDriveShaft.sim.evaluation import calc_buckling, calc_strength, calc_eigenfreq
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
    "l_thickness, l_orientations, ds_diameter, ds_length",
    [
        (1.0, [0], 10, 30),   # fkrit in N
        (1.0, [90], 20, 60),
    ]
)
def test_apdl_optimization(l_thickness,  l_orientations, ds_diameter, ds_length):
    stackup = generate_stackup(hts40_mat, l_thickness, l_orientations)
    shaft = SimpleDriveShaft(diameter=ds_diameter, length=ds_length, stackup=stackup)

    strength = calc_strength(mapdl, shaft, Loading(mz=1e3), dict())
    buck = calc_buckling(mapdl, shaft, dict(), "MOMENT")[0] * 1000
    rpm = calc_eigenfreq(mapdl, shaft, dict())[0] * 60

    opt_strength = calc_strength(mapdl, shaft, Loading(mz=1e3), dict())
    assert abs(strength - opt_strength) < 0.1

    opt_buck = calc_buckling(mapdl, shaft, None, "MOMENT")[0] * 1000
    assert abs(buck - opt_buck) < 0.1

    opt_rpm = calc_eigenfreq(mapdl, shaft, None)[0] * 60
    assert abs(rpm - opt_rpm) < 0.1
