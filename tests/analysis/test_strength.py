from src.DigitalDriveShaft.basic import TransverselyIsotropicMaterial, Ply, Stackup, Loading, CuntzeFailure
from src.DigitalDriveShaft.cylindrical import SimpleDriveShaft
from src.DigitalDriveShaft.analysis import calc_strength
import numpy as np
import pytest


# to learn more, visit: https://docs.pytest.org/en/7.1.x/how-to/fixtures.html
@pytest.fixture
def mat_HTS40():
    HTS40_cuntze = CuntzeFailure(
                                    E1=145200,  # MPa
                                    R_1t=852.0, R_1c=630.93,  # MPa
                                    R_2t=852.0, R_2c=630.93, R_21=630.93  # MPa
                                )

    HTS40_Epoxy = TransverselyIsotropicMaterial(E_l=145200,  # MPa
                                                E_t=6272.7,  # MPa
                                                nu_lt=0.28,  # MPa
                                                nu_tt=0.28,
                                                G_lt=2634.2,  # MPa
                                                G_tt=2634.2,
                                                density=1.58,  # g/cm^3
                                                failures=[HTS40_cuntze])  # MPa
    return HTS40_Epoxy


@pytest.fixture
def generate_stackup(mat_HTS40):
    ply_0 = Ply(material=mat_HTS40,
           thickness=10.1/4)

    ply_45 = ply_0.rotate(45, degree=True)  # 45°
    ply_n45 = ply_0.rotate(45, degree=True)  # -45°
    # ply90 = ply0.rotate(np.pi/2)  # 90°
    stackup = Stackup([ply_45, ply_n45, ply_45, ply_45])
    return stackup


@pytest.fixture
def shaft(generate_stackup):
    shaft = SimpleDriveShaft(diameter=85.5*2, length=100, stackup=generate_stackup)
    return shaft


@pytest.mark.parametrize(
    "loading, result_stress",
    [
        (Loading(mz=168960),  630.3)
    ]
)  # to learn more visit: https://docs.pytest.org/en/7.1.x/example/parametrize.html
def test_stress(shaft, loading, result_stress):
    result = calc_strength(shaft, loading)
    assert result == result_stress