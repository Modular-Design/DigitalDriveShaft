from src.DigitalDriveShaft.basic import TransverselyIsotropicMaterial, IsotropicMaterial, Ply, Stackup, Loading, CuntzeFailure
from src.DigitalDriveShaft.cylindrical import SimpleDriveShaft
from src.DigitalDriveShaft.analysis import calc_crit_moment
from src.DigitalDriveShaft.sim.evaluation import calc_buckling
import pytest
from ansys.mapdl.core import launch_mapdl


steel = IsotropicMaterial(30e6, 0.3, 7.874)

hts40_mat = TransverselyIsotropicMaterial(E_l=145200,  # MPa
                                          E_t=6272.7,  # MPa
                                          nu_lt=0.28,  # MPa
                                          G_lt=2634.2,  # MPa
                                          density=1.58,  # g/cm^3
                                          )  # MPa


def generate_stackup(mat, layer_thickness, deg_orientations):
    plies = []
    for orientation in deg_orientations:
        plies.append(Ply(mat, layer_thickness, orientation, degree=True))

    return Stackup(plies)


mapdl = launch_mapdl(mode="grpc", loglevel="ERROR")


def test_apdl_reference():
    """

    Returns
    -------

    Notes
    -----
    APDL Reference p.1413
    """
    mapdl.clear()
    mapdl.finish()
    mapdl.prep7()
    mapdl.mp('EX', 1, 30e6)
    mapdl.mp('PRXY', 1, 0.3)
    mapdl.et(1, 'BEAM188')
    mapdl.keyopt(1, 3, 3)
    mapdl.sectype(1, "BEAM", "RECT")
    mapdl.secdata(0.5, 0.5)
    mapdl.n(1)
    mapdl.n(11, "", 100)
    mapdl.fill()
    mapdl.e(1, 2)
    mapdl.egen(10, 1, 1)
    # mapdl.eplot(show_node_numbering=True, show_edges=True)
    mapdl.d('ALL', lab='UZ', lab2='ROTX', lab3='ROTY')
    # shaft = SimpleDriveShaft(0.5, 100, Stackup([Ply(hts40_mat, 1)]))
    # result = calc_buckling(mapdl, shaft, None, "FORCE")
    mapdl.finish()
    mapdl.slashsolu()
    mapdl.antype("STATIC")
    mapdl.pstres("ON")
    mapdl.d(1, "ALL")
    mapdl.f(11, "FY", -1)
    mapdl.solve()
    mapdl.finish()

    mapdl.slashsolu()
    mapdl.antype("BUCKLE")
    mapdl.bucopt("LANB", 3)
    mapdl.mxpand(3)
    mapdl.solve()
    result = mapdl.get('FCR1', 'MODE', 1, 'FREQ')
    # mapdl.get('FCR1', 'MODE', 2, 'FREQ')
    # mapdl.get('FCR1', 'MODE', 3, 'FREQ')

    assert abs(38.533 - result) < 0.1


def test_isotropic_buckling():
    mapdl.clear()
    mapdl.finish()
    mapdl.prep7()
    shaft = SimpleDriveShaft(0.5, 100, Stackup([Ply(steel, 1)]))
    result = calc_buckling(mapdl, shaft, {"element_type": "SHELL"}, "FORCE")
    assert abs(38.533 - result) < 0.1


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
        (1.0, [90], 10, 300),
        # (15.58/4, [45, -45, -45, 45], 79.42*2, 400),
        # (11.02/7, [45, -45, 90, 0, 90, -45, 45], 79.42*2, 400),
    ]
)
def test_analytic_vs_sim(l_thickness, l_orientations, ds_diameter, ds_length):
    stackup = generate_stackup(hts40_mat, l_thickness, l_orientations)
    shaft = SimpleDriveShaft(diameter=ds_diameter, length=ds_length, stackup=stackup)
    sim = calc_buckling(mapdl, shaft, dict(), "MOMENT")[0] * 1000  # [Nmm]
    analytic = calc_crit_moment(shaft)
    assert abs(sim - analytic) < 0.01
