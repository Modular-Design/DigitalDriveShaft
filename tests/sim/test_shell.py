import pytest
from pymaterial.materials import TransverselyIsotropicMaterial
from pymaterial.combis.clt import Ply
from src.DigitalDriveShaft.sim import material_to_mapdl
from src.DigitalDriveShaft.sim.elements import Shell181
from ansys.mapdl.core import launch_mapdl
import numpy as np

# default ElamX 2.6 Material
material = TransverselyIsotropicMaterial(
    E_l=141000.0, E_t=9340.0, nu_lt=0.35, G_lt=4500.0, density=1.7e-6  # N/mm^2
)  # kg/mm^3

mapdl = launch_mapdl(mode="grpc", loglevel="ERROR")


def shell_tests(laminat, system, stresses, significance):
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
        # print(f"Rotation: {lam.get_rotation(degree=True)}")
        shell.add_layer(lam.thickness, mat_id, lam.get_rotation(degree=True) + 90.0)
        mat_id += 1
    shell.add_to_mapdl(mapdl)

    mapdl.asel("S", "AREA", "", 1)
    mapdl.esize(0, 1)
    mapdl.type(elem_id)
    mapdl.secnum(elem_id)
    mapdl.amesh("ALL")

    mapdl.run("/solu")
    # fixation
    mapdl.nsel("S", "LOC", "Y", 0)
    mapdl.d("ALL", "UY", 0)
    mapdl.d("ALL", "UZ", 0)
    mapdl.nsel("S", "LOC", "Y", 1)
    mapdl.d("ALL", "UY", 0)
    mapdl.d("ALL", "UZ", 0)

    mapdl.nsel("S", "LOC", "X", 0)
    mapdl.d("ALL", "UX", 0)
    mapdl.d("ALL", "UY", 0)
    mapdl.d("ALL", "UZ", 0)

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
    if system == "local":
        mapdl.rsys("LSYS")  # stress in coordinate system
    elif system == "global":
        mapdl.rsys(0)
    else:
        raise ValueError(f"system is neither 'local' nor 'global' (got: '{system}')!")

    for i in range(len(laminat)):
        mapdl.layer(i + 1)

        sol_bot, sol_top = stresses[i]
        sign_bot, sign_top = significance[i]

        mapdl.shell("bot")
        x_stresses = mapdl.post_processing.element_stress(
            "X"
        )  # nodal_component_stress('X')
        sx_max_bot = float(np.nanmax(x_stresses))
        y_stresses = mapdl.post_processing.element_stress(
            "Y"
        )  # nodal_component_stress('Y')
        sy_max_bot = float(np.nanmax(y_stresses))
        txy_stresses = mapdl.post_processing.element_stress("XY")
        txy_max_bot = float(np.nanmax(txy_stresses))
        # print(f"bot: {sx_max_bot} | {sy_max_bot} | {txy_max_bot}")

        mapdl.shell("top")
        x_stresses = mapdl.post_processing.element_stress("X")
        sx_max_top = float(np.nanmax(x_stresses))
        y_stresses = mapdl.post_processing.element_stress(
            "Y"
        )  # nodal_component_stress('X')
        sy_max_top = float(np.nanmax(y_stresses))
        txy_stresses = mapdl.post_processing.element_stress("XY")
        txy_max_top = float(np.nanmax(txy_stresses))
        # print(f"top: {sx_max_top} | {sy_max_top} | {txy_max_top}")

        assert round(sx_max_bot, sign_bot[0]) == round(sol_bot[0], sign_bot[0])
        assert round(sy_max_bot, sign_bot[1]) == round(sol_bot[1], sign_bot[1])
        assert round(txy_max_bot, sign_bot[2]) == round(sol_bot[2], sign_bot[2])

        assert round(sx_max_top, sign_top[0]) == round(sol_top[0], sign_top[0])
        assert round(sy_max_top, sign_top[1]) == round(sol_top[1], sign_top[1])
        assert round(txy_max_top, sign_top[2]) == round(sol_top[2], sign_top[2])


@pytest.mark.slow
def test_shell():
    # parameter = "laminat, system, stresses, significance",
    # # stresses list of layer stress bot -> top (bot, top)
    params = [
        (
            [Ply(material, 1, 0)],
            "local",
            [((142153.51, 3295.743, 0.0), (142153.51, 3295.743, 0.0))],
            [((-3, -2, 1), (-3, -2, 1))],
        ),
        (
            [Ply(material, 1, 0)],
            "global",
            [((142153.51, 3295.743, 0.0), (142153.51, 3295.743, 0.0))],
            [((-3, -2, 1), (-3, -2, 1))],
        ),
        (
            [Ply(material, 1, 90, degree=True)],
            "local",
            [((3295.743, 9416.41, 0.0), (3295.743, 9416.41, 0.0))],
            [((-3, -2, 1), (-3, -2, 1))],
        ),
        (
            [Ply(material, 1, 90, degree=True)],
            "global",
            [((9416.41, 3295.743, 0.0), (9416.41, 3295.743, 0.0))],
            [((-3, -2, 1), (-3, -2, 1))],
        ),
        # (
        #     [Ply(material, 1, 45, degree=True)], "local",
        #     [((72724.627, 6356.077, -4500), (72724.627, 6356.077, -4500))],
        #     [((-3, -2, 1), (-3, -2, 1))]
        # ),
        (
            [Ply(material, 1, 90, degree=True), Ply(material, 1, 0)],
            "local",
            [
                ((-500.872, 21620.41, 0.0), (3295.743, 9416.41, 0.0)),
                ((142153.51, 3295.743, 0.0), (-44747.727, -502.872, 0.0)),
            ],
            [((-2, -2, 1), (-3, -2, 1)), ((-3, -2, 1), (-3, -2, 1))],
        ),
    ]

    for param in params:
        shell_tests(*param)

    mapdl.exit()
