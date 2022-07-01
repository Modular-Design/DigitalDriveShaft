from src.DigitalDriveShaft.basic import IsotropicMaterial, Stackup, Ply

from src.DigitalDriveShaft.cylindrical import DriveShaft, CylindricalForm, CylindricalStackup
import pytest
import numpy as np

dens1_mat = IsotropicMaterial(1, 0.3, 1)
dens10_mat = IsotropicMaterial(1, 0.3, 10)


def mix_mats_on_z(z: float, z_crit: float):
    if z <= z_crit:
        return dens1_mat
    return dens10_mat


@pytest.mark.parametrize(
    "form, stackup, pos_z, pos_phi, iso, radians, err",
    [
        (
                CylindricalForm(lambda z, phi: 10 + z, 20),
                CylindricalStackup(lambda z, phi: Stackup([Ply(dens1_mat, 1 + 0.5 * z)])),
                0, 0, False, (10, 11), 1e-2
        ),
        (
                CylindricalForm(lambda z, phi: 10 + z, 20),
                CylindricalStackup(lambda z, phi: Stackup([Ply(dens1_mat, 1 + 0.5 * z)])),
                20, 0, False, (30, 41), 1e-2
        ),
        (
                CylindricalForm(lambda z, phi: 10 + z, 20),
                CylindricalStackup(lambda z, phi: Stackup([Ply(dens1_mat, 1 + 10 * z)])),  # z in [0, 1]
                1.0, 0, True, (30, 41), 1e-2
        ),

    ]
)
def test_get_radius(form, stackup, pos_z, pos_phi, iso, radians, err):
    shaft = DriveShaft(form, stackup, 0)
    result_inner = shaft.get_radius(pos_z, pos_phi, 0.0, iso)
    result_outer = shaft.get_radius(pos_z, pos_phi, 1.0, iso)
    assert np.fabs(result_inner - radians[0]) <= err
    assert np.fabs(result_outer - radians[1]) <= err


@pytest.mark.parametrize(
    "form, stackup, pos_z, crossection, err",
    [
        (
                CylindricalForm(lambda z, phi: 10, 1),
                CylindricalStackup(lambda z, phi: Stackup([Ply(dens1_mat, 1)])),
                0, 65.9734, 1e-2
        ),  # int int r dr dphi phi=0..2pi r=10..11
        (
                CylindricalForm(lambda z, phi: 10, 1),
                CylindricalStackup(lambda z, phi: Stackup([Ply(dens1_mat, 3)])),
                0, 216.77, 1e-2
        ),  # int int r dr dphi phi=0..2pi r=10..13
        (
                CylindricalForm(lambda z, phi: 5, 1),
                CylindricalStackup(lambda z, phi: Stackup([Ply(dens1_mat, 5)])),
                0, 235.619, 1e-2
        ),  # int int r dr dphi phi=0..2pi r=5..10
    ]
)
def test_get_crossection(form, stackup, pos_z, crossection, err):
    shaft = DriveShaft(form, stackup, 0)
    result = shaft.get_cross_section(pos_z)
    assert np.fabs(result - crossection) <= err


@pytest.mark.parametrize(
    "form, stackup, pos_z, iso, area_mass, err",
    [
        (
                CylindricalForm(lambda z, phi: 10, 20),
                CylindricalStackup(lambda z, phi: Stackup([Ply(dens1_mat, 1)])),
                0, True, 65.9734, 1e-2
        ),  # int int r dr dphi phi=0..2pi r=10..11
        (
                CylindricalForm(lambda z, phi: 10, 20),
                CylindricalStackup(lambda z, phi: Stackup([Ply(dens1_mat, 3)])),
                0, True, 216.77, 1e-2
        ),  # int int 11 r dr dphi phi=0..2pi r=10..13
        (
                CylindricalForm(lambda z, phi: 5, 1),
                CylindricalStackup(lambda z, phi: Stackup([Ply(dens1_mat, 5)])),
                0, True, 235.619, 1e-2
        ),  # int int r dr dphi phi=0..2pi r=5..10
        (
                CylindricalForm(lambda z, phi: 10, 20),
                CylindricalStackup(lambda z, phi: Stackup([Ply(dens10_mat, 1)])),
                0, True, 659.734, 1e-2
        ),  # int int 10 r dr dphi phi=0..2pi r=10..11
        (
                CylindricalForm(lambda z, phi: 5, 20),
                CylindricalStackup(lambda z, phi: Stackup([Ply(dens10_mat, 1), Ply(dens1_mat, 3)])),
                1.0, True, 486.947, 1e-2
        ),  # int int 10 r dr dphi phi=0..2pi r=5..6 + int int 1 r dr dphi phi=0..2pi r=6..9
        (
                CylindricalForm(lambda z, phi: 10, 10, 0),
                CylindricalStackup(lambda z, phi: Stackup([Ply(mix_mats_on_z(z, 10), 1)]), 10, 0),
                2.0, False, 65.9734, 1e-1
        ),  # int int 1 * r dr dphi phi=0..2pi r=10..11
    ]
)
def test_get_area_mass(form, stackup, pos_z, iso, area_mass, err):
    shaft = DriveShaft(form, stackup, 0)
    result = shaft.get_area_mass(pos_z, iso)
    assert np.fabs(result - area_mass) <= err


@pytest.mark.parametrize(
    "form, stackup, volume, err",
    [
        (
                CylindricalForm(lambda z, phi: 10, 20),
                CylindricalStackup(lambda z, phi: Stackup([Ply(dens1_mat, 1)])),
                1319.47, 1e-2
        ),  # int int int r dr dphi dz phi=0..2pi r=10..11 z=0..20
        (
                CylindricalForm(lambda z, phi: 10 + 2 * z, 20),
                CylindricalStackup(lambda z, phi: Stackup([Ply(dens1_mat, 1)])),
                3832.74, 1e-2
        ),  # int int int r dr dphi dz phi=0..2pi r={10+2*z}..{10+2*z+1} z=0..20
        (
                CylindricalForm(lambda z, phi: 5 + 2 * z, 20),
                CylindricalStackup(lambda z, phi: Stackup([Ply(dens1_mat, 1 + 0.5 * z)]), 20),
                25823.9, 1
        ),  # int int int r dr dphi dz phi=0..2pi r={5+2*z}..{5+2*z+{1+0.5*z}} z=0..20
    ]
)
def test_get_volume(form, stackup, volume, err):
    shaft = DriveShaft(form, stackup, 0)
    result = shaft.get_volume()
    assert np.fabs(result - volume) <= err


@pytest.mark.parametrize(
    "form, stackup, density, err",
    [
        (
                CylindricalForm(lambda z, phi: 10, 20),
                CylindricalStackup(lambda z, phi: Stackup([Ply(dens1_mat, 1)])),
                1319.47, 1e-2
        ),  # int int int 1 * r dr dphi dz phi=0..2pi r=10..11 z=0..20
        (
                CylindricalForm(lambda z, phi: 10, 20),
                CylindricalStackup(lambda z, phi: Stackup([Ply(dens10_mat, 1)])),
                13194.7, 1e-1
        ),  # int int int 10 * r dr dphi dz phi=0..2pi r=10..11 z=0..20
        (
                CylindricalForm(lambda z, phi: 10, 10, 0),
                CylindricalStackup(lambda z, phi: Stackup([Ply(mix_mats_on_z(z, 10), 1)]), 10, 0),
                659.734, 1e-1
        ),  # {int int int 1 * r dr dphi dz phi=0..2pi r=10..11 z=0..10}
        (
                CylindricalForm(lambda z, phi: 10, 20, 10),
                CylindricalStackup(lambda z, phi: Stackup([Ply(mix_mats_on_z(z, 9), 1)]), 20, 10),
                6597.34, 1e-1
        ),  # {int int int 10 * r dr dphi dz phi=0..2pi r=10..11 z=10..20}
        # (
        #         CylindricalForm(lambda z, phi: 10, 20),
        #         CylindricalStackup(lambda z, phi: Stackup([Ply(mix_mats_on_z(z, 10), 1)]), 20),
        #         7257.08, 1e-1
        # ) # {int int int 1 * r dr dphi dz phi=0..2pi r=10..11 z=0..10} + {int int int 10 * r dr dphi dz phi=0..2pi r=10..11 z=10..20}
    ]
)
def test_get_mass(form, stackup, density, err):
    shaft = DriveShaft(form, stackup, 0)
    result = shaft.get_mass()
    assert np.fabs(result - density) <= err



@pytest.mark.parametrize(
    "form, stackup, density, err",
    [
        (
                CylindricalForm(lambda z, phi: 10, 20),
                CylindricalStackup(lambda z, phi: Stackup([Ply(dens1_mat, 1)])),
                1.0, 1e-2
        ),  # int int int r dr dphi dz phi=0..pi r=10..11 z=0..20
        (
                CylindricalForm(lambda z, phi: 10, 20),
                CylindricalStackup(lambda z, phi: Stackup([Ply(dens10_mat, 1)])),
                10.0, 1e-2
        ),
        (
                CylindricalForm(lambda z, phi: 5, 20),
                CylindricalStackup(lambda z, phi: Stackup([Ply(dens10_mat, 1), Ply(dens1_mat, 3)])),
                2.76786, 1e-2
        ),  # (int int 10 r dr dphi phi=0..2pi r=5..6 + int int 1 r dr dphi phi=0..2pi r=6..9) / (int int r dr dphi phi=0..2pi r=5..9)
        # (
        #         CylindricalForm(lambda z, phi: 10, 20),
        #         CylindricalStackup(lambda z, phi: Stackup([Ply(mix_mats_on_z(z, 0.5), 1)])),
        #         6.5, 1e-2
        # )
    ]
)
def test_get_density(form, stackup, density, err):
    shaft = DriveShaft(form, stackup, 0)
    result = shaft.get_density()
    assert np.fabs(result - density) <= err

