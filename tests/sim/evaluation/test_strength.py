from src.DigitalDriveShaft.basic import TransverselyIsotropicMaterial, Ply, Stackup, Loading, CuntzeFailure
from src.DigitalDriveShaft.cylindrical import SimpleDriveShaft
from src.DigitalDriveShaft.sim.evaluation import calc_strength
import src.DigitalDriveShaft.analysis as analysis
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


@pytest.mark.parametrize(
    "l_thickness, l_orientations, ds_diameter, ds_length, loading",
    [
        (1.0, [90], 10, 30, Loading(fz=100)),
        (1.0, [0, 90], 10, 30, Loading(fz=100)),
        (1.0, [0], 10, 30, Loading(mz=100)),
        (10.1/4, [45, -45, -45, 45], 85.5*2, 100, Loading(mz=168960)),
        (11.02/7, [45, -45, 90, 0, 90, -45, 45], 79.42*2, 400, Loading(mz=20000)),
    ]
)
def test_analytic_vs_sim(l_thickness, l_orientations, ds_diameter, ds_length, loading):
    stackup = generate_stackup(hts40_mat, l_thickness, l_orientations)
    shaft = SimpleDriveShaft(diameter=ds_diameter, length=ds_length, stackup=stackup)
    sim = calc_strength(mapdl, shaft, loading, dict(n_z=10, n_phi=30))
    _, stresses, failures = analysis.calc_static_porperties(shaft, loading)
    analytic = analysis.calc_strength(failures)
    assert abs(sim - analytic) < 0.01
