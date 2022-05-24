import pytest
from src.DigitalDriveShaft.basic import TransverselyIsotropicMaterial, Ply

material = TransverselyIsotropicMaterial(E_l=141000.0, E_t=9340.0,
                                         nu_lt=0.35,
                                         G_lt=4500.0, density=1.7E-9)


@pytest.mark.slow
@pytest.mark.parametrize(
    "laminat, stress",
    [
        ([Ply(material, 1, 0)], round(1.0 / 141.00, 1)),
        ([Ply(material, 1, 90, degree=True)], round(1.0 / 9.34, 1))
    ]
)
def test_shell(laminat, stress):
    raise NotImplementedError
