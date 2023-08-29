from DigitalDriveShaft.cylindrical import DriveShaft
from ..cylindrical import driveshaft_to_mapdl
from ansys.mapdl.core import Mapdl
from typing import Optional, Literal
import matplotlib.pyplot as plt


def calc_buckling(
    mapdl: Mapdl,
    shaft: DriveShaft,
    mesh_builder: Optional[dict] = None,
    load_mode: Literal["FORCE", "MOMENT"] = "MOMENT",
) -> float:
    """

    Parameters
    ----------
    mapdl
    shaft
    load
    mesh_builder: dict
        dictionary might containing:
            "n_z",
            "phi_max",
            "phi_min" (both in [DEG]),
            "n_phi"

    load_mode: str

    Returns
    -------
    min_safety

    Notes
    -----
    ANSYS Mechanical APDL Verification Manual
    VM127: Buckling of a Bar with Hinged Ends (Line Elements) p.373
    """

    mapdl.finish()
    if mesh_builder is not None:
        mapdl.clear()
        mapdl.prep7()
        driveshaft_to_mapdl(
            mapdl, shaft, element_type="SHELL", mesh_builder=mesh_builder
        )
        mapdl.asel("ALL")
        mapdl.nummrg("NODE")

    # BCs
    # Fixation
    mapdl.csys(0)
    mapdl.nsel("S", "LOC", "Z", 0)
    mapdl.d("ALL", "UX", 0)
    mapdl.d("ALL", "UY", 0)
    mapdl.d("ALL", "UZ", 0)
    mapdl.d("ALL", "ROTX", 0)
    mapdl.d("ALL", "ROTY", 0)
    mapdl.d("ALL", "ROTZ", 0)
    mapdl.nsel("ALL")
    mapdl.allsel()

    # Loading
    length = shaft.get_length()
    mapdl.nsel("S", "LOC", "Z", length)
    # nodes = mapdl.mesh.nodes
    if load_mode == "FORCE":
        mapdl.d("ALL", "UZ", -10)
        mapdl.d("ALL", "UX", 1)  # imperfection
        mapdl.allsel()

    elif load_mode == "MOMENT":
        mapdl.csys(1)
        mapdl.d("ALL", "UY", 10)
        mapdl.csys(0)
    else:
        raise ValueError(
            "load_mode is nether 'FORCE' or 'MOMENT'! "
            + f"(load_mode is: '{load_mode}')"
        )
    mapdl.allsel("ALL")
    mapdl.nsel("ALL")

    # source: https://homepage.tudelft.nl/p3r3s/bsc_projects/eindrapport_hogendoorn.pdf
    # compute linear  elastic
    mapdl.slashsolu()
    # mapdl.antype("TRANS")
    mapdl.antype("static")
    mapdl.nlgeom("ON")
    mapdl.autots("ON")
    mapdl.time(1)
    mapdl.nsubst(50, 100, 50)
    # mapdl.pstres('ON')
    mapdl.outres("ALL", "ALL")
    # mapdl.nladaptive()
    mapdl.allsel("ALL")
    try:
        mapdl.solve()
    except Exception:
        raise RuntimeError(
            "Large deformations detected inside elements! " "Please refine mesh!"
        )
    mapdl.finish()

    mapdl.post1()
    result = mapdl.result

    loads = []
    for i in range(1, result.n_results + 1):
        mapdl.set(1, i)
        mapdl.nsel("S", "LOC", "Z", 0)
        # mapdl.rforce()
        mapdl.csys(1)
        mapdl.fsum()
        if load_mode == "FORCE":
            loads.append(-1 * mapdl.get_value("FSUM", "", "ITEM", "FZ"))
        elif load_mode == "MOMENT":
            loads.append(-1 * mapdl.get_value("FSUM", "", "ITEM", "MZ"))
        mapdl.csys(0)
        #
        # loads.append(mapdl.get("REAC_1", "FSUM", "", "ITEM", "FZ"))
        # mapdl.result.plot_nodal_displacement(i - 1, show_displacement=True,
        #                                     displacement_factor=1.0,
        #                                     show_edges=True, vtk=True,
        #                                     )
        result.plot_nodal_displacement(
            show_displacement=True,
            displacement_factor=1.0,
            show_edges=True,
            vtk=True,
        )
        # """
    print(loads)

    fig, ax = plt.subplots()
    ax.plot(result.time_values, loads)
    plt.show()

    crit = max(loads)
    if loads[0] > crit or loads[-1] > crit:
        raise RuntimeError("No critical loading detected! Increase maximum steps!")

    return max(loads)
