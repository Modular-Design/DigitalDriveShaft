import pytest
from src.DigitalDriveShaft.basic import TransverselyIsotropicMaterial, Ply
from src.DigitalDriveShaft.sim import material_to_mapdl
from src.DigitalDriveShaft.sim.elements import Shell181
from ansys.mapdl.core import launch_mapdl
import numpy as np

# default ElamX 2.6 Material
material = TransverselyIsotropicMaterial(E_l=141000.0, E_t=9340.0,
                                         nu_lt=0.35,
                                         G_lt=4500.0, density=1.7E-9)


@pytest.mark.slow
@pytest.mark.parametrize(
    "laminat, stress",
    [
        ([Ply(material, 1, 0)], round(141000, 1)),
        # ([Ply(material, 1, 90, degree=True)], round(1.0 / 9.34, 1))
    ]
)
def test_shell(laminat, stress):
    mapdl = launch_mapdl(mode="grpc", loglevel="ERROR")
    mapdl.finish()
    mapdl.clear()
    mapdl.verify()

    mapdl.prep7()

    """
    
        2 - 3
    y   |   |
    ^   1 - 4
    |
    +-> x
    """
    p1 = mapdl.k(1, 0, 0, 0)
    p2 = mapdl.k(2, 0, 1, 0)
    p3 = mapdl.k(3, 1, 1, 0)
    p4 = mapdl.k(4, 1, 0, 0)
    mapdl.a(p1, p2, p3, p4)

    elem_id = 1
    shell = Shell181(elem_id)

    mat_id = 1
    for lam in laminat:
        material_to_mapdl(mapdl, lam.material, mat_id)
        shell.add_layer(lam.thickness, mat_id, lam.get_rotation(degree=True))
        mat_id += 1
    shell.add_to_mapdl(mapdl)

    mapdl.asel("S", "AREA", '', elem_id)
    mapdl.esize(0, 1)
    mapdl.type(elem_id)
    mapdl.secnum(elem_id)
    mapdl.amesh("ALL")

    mapdl.run("/solu")
    # fixation
    mapdl.nsel("S", "LOC", "X", 0)
    mapdl.d("ALL", "UX", 0)
    mapdl.d("ALL", "UY", 0)
    mapdl.d("ALL", "UZ", 0)
    mapdl.nsel("S", "LOC", "Y", 0)
    mapdl.d("ALL", "ALL", 0)

    # loading
    mapdl.nsel("S", "LOC", "X", 1)
    mapdl.d("ALL", "UX", 1)
    # mapdl.sfl("ALL", "PRES", - 1)

    # select everything before solving
    mapdl.allsel()

    mapdl.antype("STATIC")
    mapdl.outres("ALL", "ALL")
    mapdl.solve()
    mapdl.finish()

    mapdl.post1()
    mapdl.set(1)
    # mapdl.post_processing.plot_nodal_eqv_stress()
    mapdl.post_processing.plot_nodal_principal_stress('1',
                                                      cpos='iso', window_size=[1024, 512])

    mapdl.post_processing.plot_nodal_elastic_principal_strain('1',
                                                              cpos='iso', window_size=[1024, 512])
    result = mapdl.result
    nodenump, stress = result.principal_nodal_stress(0)

    s1max = np.nanmax(stress[:, -5])
    # s2max = np.nanmax(stress[:, -4])

    assert s1max == stress
    mapdl.exit()


@pytest.mark.slow
def test_shell_stress():
    mapdl = launch_mapdl(mode="grpc", loglevel="ERROR")
    mapdl.finish()
    mapdl.prep7()

    p1 = mapdl.k(1, 0, 0, 0)
    p2 = mapdl.k(2, 0, 1, 0)
    p3 = mapdl.k(3, 1, 1, 0)
    p4 = mapdl.k(4, 1, 0, 0)
    mapdl.a(p1, p2, p3, p4)

    # define material 1
    mat_id1 = 1
    mapdl.mp("EX", mat_id1, 1e5)
    mapdl.mp("PRXY", mat_id1, 0.3)

    # define material 2
    mat_id2 = 2
    mapdl.mp("EX", mat_id2, 2e5)
    mapdl.mp("PRXY", mat_id2, 0.3)

    elem_id = 1
    mapdl.et(elem_id, "SHELL181")
    mapdl.sectype(elem_id, type_="SHELL", name=f"shell181_{elem_id}")
    mapdl.secdata(1, mat_id1, 0, 5)  # one layer of material 1 with 1 thickness
    mapdl.secdata(1, mat_id2, 0, 5)  # one layer of material 2 with 1 thickness

    # meshing
    mapdl.asel("S", "AREA", '', elem_id)
    mapdl.esize(0, 1)
    mapdl.type(elem_id)
    mapdl.secnum(elem_id)
    mapdl.amesh("ALL")

    mapdl.run("/solu")

    # fixation
    mapdl.nsel("S", "LOC", "X", 0)
    mapdl.d("ALL", "UX", 0)
    mapdl.d("ALL", "UY", 0)
    mapdl.d("ALL", "UZ", 0)
    mapdl.nsel("S", "LOC", "Y", 0)
    mapdl.d("ALL", "ALL", 0)

    # loading
    mapdl.nsel("S", "LOC", "X", 1)
    mapdl.d("ALL", "UX", 1)  # strain bc

    # select everything before solving
    mapdl.allsel()
    mapdl.antype("STATIC")
    mapdl.outres("ALL", "ALL")
    mapdl.solve()
    mapdl.finish()
    mapdl.post1()
    mapdl.set(1)

    result = mapdl.result

    # this does not work
    nodenump, stress = result.principal_nodal_stress(0)
    s1max = np.nanmax(stress[:, -5])