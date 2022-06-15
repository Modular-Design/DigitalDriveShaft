from src.DigitalDriveShaft.basic import TransverselyIsotropicMaterial, Ply, Stackup, Loading, CuntzeFailure
from src.DigitalDriveShaft.cylindrical import SimpleDriveShaft
from src.DigitalDriveShaft.analysis import calc_static_porperties, get_relevant_value, calc_strength, calc_buckling, calc_dynamic_stability
import pytest


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


# l - Layer
# ds - DriveShaft
@pytest.mark.skip(reason="test is not finished yet.")
@pytest.mark.parametrize(
    "l_thickness, l_orientations, ds_diameter, ds_length, loading, result_safety_beulen",
    [
        (15.58/4, [45, -45, -45, 45], 79.42*2, 400, Loading(mz=168960),  3.6),   # mz in Nm #RPM_crit_Stackup1 = 98839  # u/min
        (11.02/7, [45, -45, 90, 0, 90, -45, 45], 79.42*2, 400, Loading(mz=168960),  3.6)   # mz in Nm  #RPM_crit_Stackup2 = 197439  # u/min
    ]
)
def test_buckling(l_thickness, l_orientations, ds_diameter, ds_length, loading, result_safety_beulen):
    stackup = generate_stackup(hts40_mat, l_thickness, l_orientations)
    shaft = SimpleDriveShaft(diameter=ds_diameter, length=ds_length, stackup=stackup)
    safety_beulen = calc_buckling(shaft, loading)
    assert safety_beulen == result_safety_beulen


# l - Layer
# ds - DriveShaft
@pytest.mark.skip(reason="test is not finished yet.")
@pytest.mark.parametrize(
    "l_thickness, l_orientations, ds_diameter, ds_length, loading, result_safety_dyn_stability",
    [
        (15.58/4, [45, -45, -45, 45], 79.42*2, 400, Loading(mz=168960),  15),   # mz in Nm
        (15.58/4, [45, -45, -45, 45], 79.42*2, 400, Loading(mz=168960),  29.9)   # mz in Nm
    ]
)
def test_dyn_stability(l_thickness, l_orientations, ds_diameter, ds_length, loading, result_safety_dyn_stability):
    stackup = generate_stackup(hts40_mat, l_thickness, l_orientations)
    shaft = SimpleDriveShaft(diameter=ds_diameter, length=ds_length, stackup=stackup)
    safety_dyn_stability = calc_dynamic_stability(shaft, loading)
    assert safety_dyn_stability == result_safety_dyn_stability
