import pytest
from src.DigitalDriveShaft.basic import Ply, TransverselyIsotropicMaterial, Stackup
import numpy as np

material = TransverselyIsotropicMaterial(E_l=141000.0, E_t=9340.0,
                                         nu_lt=0.35,
                                         G_lt=4500.0, density=1.7E-9)

@pytest.mark.parametrize(
    "plies, a_mat",
    [
        ([Ply(material, 1.0, 0)], np.array([[142153.5, 3295.7, 0.0],
                                            [3295.7, 9416.4, 0.0],
                                            [0.0, 0.0, 4500.0]])),
        ([Ply(material, 1.0, 45.0, degree=True)], np.array([[44040.4, 35040.4, 33184.3],
                                                            [35040.4, 344040.4, 33184.3],
                                                            [33184.3, 33184.3, 36244.6]])),
        ([Ply(material, 1.0, -45.0, degree=True)], np.array([[44040.4, 35040.4, -33184.3],
                                                             [35040.4, 344040.4, -33184.3],
                                                             [-33184.3, -33184.3, 36244.6]]))
    ]
)
def test_abd_a(plies: list, a_mat):
    abd = Stackup(plies).get_abd()
    for i in range(3):
        for j in range(3):
            assert round(abd[i, j], 1) == a_mat[i, j]
