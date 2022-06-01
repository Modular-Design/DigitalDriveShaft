from src.DigitalDriveShaft.basic import TransverselyIsotropicMaterial, Ply, Stackup, Loading, CuntzeFailure
from src.DigitalDriveShaft.cylindrical import SimpleDriveShaft
from src.DigitalDriveShaft.analysis import calc_static_porperties, get_relevant_value, calc_strength
import pytest


@pytest.mark.parametrize(
    "values, compr, result",
    [
        ([0.0, [1, 2, 3], [4, 5, 6]], max, 6),
        ([0.0, [1, 2, 3], [4, 5, 6]], min, 0),
        ([{"max-stress": 2.0}, [{"max-stress": 1.0}, {"max-stress": 0.0}]], max, 2.0),
        ([{"max-stress": 2.0}, [{"max-stress": 1.0}, {"max-stress": 0.0}]], min, 0.0),
    ]
)
def test_get_relevant_value(values, compr, result):
    sol = get_relevant_value(values, compr)
    assert sol == result


# to learn more, visit: https://docs.pytest.org/en/7.1.x/how-to/fixtures.html
@pytest.fixture
def mat_hts40():
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
    return hts40_mat


@pytest.fixture
def generate_stackup(mat_hts40):
    ply_0 = Ply(material=mat_hts40,
           thickness=10.1/4)

    ply_45 = ply_0.rotate(45, degree=True)  # 45°
    ply_n45 = ply_0.rotate(-45, degree=True)  # -45°
    # ply90 = ply0.rotate(np.pi/2)  # 90°
    stackup = Stackup([ply_45, ply_n45, ply_n45, ply_45])
    return stackup


@pytest.fixture
def shaft(generate_stackup):
    shaft = SimpleDriveShaft(diameter=85.5*2, length=100, stackup=generate_stackup)
    return shaft


@pytest.mark.parametrize(
    "loading, result_stress",
    [
        (Loading(mz=168960 ),  630.0)   # mz in Nm
    ]
)  # to learn more visit: https://docs.pytest.org/en/7.1.x/example/parametrize.html
def test_stress(shaft, loading, result_stress):
    _, stresses, failures = calc_static_porperties(shaft, loading)
    rel_stress = round(get_relevant_value(stresses), 0)
    assert rel_stress == result_stress


    # rel_failure = calc_strength(failures)
    # assert rel_failure == result_stress
    # FALSE: 3.106553198238891e-05 != 630.3
    # because failure is 'Auslastung', maybe:
    # 1/ 3.106553198238891e-05 == 32190.016915432232 != 630.3

