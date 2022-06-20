import pytest
from src.DigitalDriveShaft.basic import TransverselyIsotropicMaterial, Ply
from src.DigitalDriveShaft.sim import material_to_mapdl
from src.DigitalDriveShaft.sim.elements import Shell181
from ansys.mapdl.core import launch_mapdl
import numpy as np

# default ElamX 2.6 Material
material = TransverselyIsotropicMaterial(E_l=141000.0, E_t=9340.0,  # N/mm^2
                                         nu_lt=0.35,
                                         G_lt=4500.0, density=1.7E-6)  # kg/mm^3

mapdl = launch_mapdl(mode="grpc", loglevel="ERROR")


def shell_tests(laminat, stresses, significance):
    # mapdl = launch_mapdl(mode="grpc", loglevel="ERROR")
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
    shell.set_layer_storage(1)  # store bot and top

    mat_id = 1
    for lam in laminat:
        material_to_mapdl(mapdl, lam.material, mat_id)
        shell.add_layer(lam.thickness, mat_id, lam.get_rotation(degree=True) + 90.0)
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

    for i in range(len(laminat)):
        mapdl.layer(i + 1)

        sol_bot, sol_top = stresses[i]
        sign_bot, sign_top = significance[i]

        mapdl.shell('bot')
        x_stresses = mapdl.post_processing.element_stress('X')  # nodal_component_stress('X')
        sx_max = float(np.nanmax(x_stresses))
        print(sx_max)
        assert round(sx_max, sign_bot) == round(sol_bot, sign_bot)

        mapdl.shell('top')
        x_stresses = mapdl.post_processing.element_stress('X')
        sx_max = float(np.nanmax(x_stresses))
        print(sx_max)
        assert round(sx_max, sign_top) == round(sol_top, sign_bot)


@pytest.mark.slow
def test_shell():
    # parameter = "laminat, stresses, significance",  # stresses list of layer stress bot -> top (bot, top)
    params = [
        ([Ply(material, 1, 0)], [(142153.51, 142153.51)], [(-3, -3)]),
        ([Ply(material, 1, 0.1, degree=True)], [(142153.51, 142153.51)], [(-3, -3)]),
        ([Ply(material, 1, 90, degree=True)], [(9416.41, 9416.41)], [(-3, -3)]),
        ([Ply(material, 0.5, 0), Ply(material, 0.5, 0)],
         [(142153.51, 142153.51), (142153.51, 142153.51)],
         [(-3, -3), (-3, -3)]),
        # ([Ply(material, 1, 90, degree=True), Ply(material, 1, 0)],[(9416.41, 9416.41), (142153.51, 142153.51)],
        # [(-3, -3), (-3, -3)])
    ]

    for param in params:
        shell_tests(*param)

    mapdl.exit()
