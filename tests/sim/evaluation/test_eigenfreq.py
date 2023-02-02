from src.DigitalDriveShaft.basic import TransverselyIsotropicMaterial, Ply, Stackup, Loading, CuntzeFailure
from src.DigitalDriveShaft.cylindrical import SimpleDriveShaft
from src.DigitalDriveShaft.sim.evaluation import calc_eigenfreq
from src.DigitalDriveShaft.analysis import calc_crit_rpm
import pytest
from ansys.mapdl.core import launch_mapdl


hts40_mat = TransverselyIsotropicMaterial(E_l=145200*1e6,  # [MPa]
                                          E_t=6272.7*1e6,  # [MPa]
                                          nu_lt=0.28,  # [ ]
                                          G_lt=2634.2*1e6,  # [MPa]
                                          density=1.58,  # [g/cm^3]
                                          )


def generate_stackup(mat, layer_thickness, deg_orientations):
    plies = []
    for orientation in deg_orientations:
        plies.append(Ply(mat, layer_thickness, orientation, degree=True))

    return Stackup(plies)


mapdl = launch_mapdl(mode="grpc", loglevel="ERROR")


@pytest.mark.parametrize(
    "l_thickness, l_orientations, ds_diameter, ds_length, eigenfreq",
    [
        (1.0, [0], 10, 30, 1.027),  # fz in N
        (1.0, [90], 10, 30, 1.041),  # fz in N
    ]
)
def test_eigenfreq(l_thickness, l_orientations, ds_diameter, ds_length, eigenfreq):
    stackup = generate_stackup(hts40_mat, l_thickness, l_orientations)
    shaft = SimpleDriveShaft(diameter=ds_diameter, length=ds_length, stackup=stackup)
    result = calc_eigenfreq(mapdl, shaft, dict())
    assert abs(result[0] - eigenfreq) < 0.01


@pytest.mark.parametrize(
    "l_thickness, l_orientations, ds_diameter, ds_length",
    [
        # (1.0e-3, [90], 10e-3, 300e-3),
        (15.58 / 4 * 1e-3, [45, -45, -45, 45], 79.42 * 2e-3, 400e-3),
        # (11.02/7, [45, -45, 90, 0, 90, -45, 45], 79.42*2, 400),
    ]
)
def test_analytic_vs_sim(l_thickness, l_orientations, ds_diameter, ds_length):
    stackup = generate_stackup(hts40_mat, l_thickness, l_orientations)
    shaft = SimpleDriveShaft(diameter=ds_diameter, length=ds_length, stackup=stackup)
    sim = calc_eigenfreq(mapdl, shaft, dict())[0] * 60
    print(sim)

    analytic = calc_crit_rpm(shaft)
    print(analytic)
    err = abs(1 - analytic / sim)
    assert err < 0.15  # error smaller 15%
