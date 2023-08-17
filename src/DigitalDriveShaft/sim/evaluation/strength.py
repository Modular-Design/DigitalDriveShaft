from DigitalDriveShaft.cylindrical import DriveShaft
from DigitalDriveShaft.analysis import get_relevant_value, Loading
from ..cylindrical import driveshaft_to_mapdl, anaylse_stackup
from ansys.mapdl.core import Mapdl
from typing import Optional


def calc_strength(
    mapdl: Mapdl, shaft: DriveShaft, load: Loading, mesh_builder: Optional[dict] = None
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

    Returns
    -------
    min_safety
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

    # master RBE3
    length = shaft.get_length()
    mapdl.nsel("S", "LOC", "Z", length)

    master_id = mapdl.n("", 0, 0, length)
    master_enum = mapdl.et("", "MASS21")
    mapdl.real(master_enum)
    mapdl.type(master_enum)
    mapdl.r(master_enum, 1.0e-9, 1.0e-9, 1.0e-9)
    mapdl.e(master_id)
    mapdl.nsel("S", "NODE", "", master_id)
    mapdl.cm("master", "NODE")

    mapdl.nsel("S", "LOC", "Z", length)
    mapdl.rbe3(master_id, "ALL", "ALL")

    # BCs
    mapdl.run("/solu")
    # Fixation
    mapdl.csys(1)
    mapdl.nsel("S", "LOC", "Z", 0)
    mapdl.d("ALL", "UY", 0)
    mapdl.d("ALL", "UZ", 0)
    mapdl.d("ALL", "UX", 0)
    mapdl.nsel("ALL")

    # Loading
    mapdl.cmsel("S", "master")
    mapdl.f("ALL", "FX", load.fx)
    mapdl.f("ALL", "FY", load.fy)
    mapdl.f("ALL", "FZ", load.fz)
    mapdl.f("ALL", "MZ", load.mz)

    mapdl.csys(1)

    # radius = shaft.get_center_radius(length, 0, False)
    # mapdl.lsel("S", "LOC", "Z", length)
    # mapdl.sfl("ALL", "PRES", - 1 / (2 * np.pi * radius))
    mapdl.nsel("ALL")

    # Solver
    mapdl.antype("STATIC")
    mapdl.outres("ALL", "ALL")
    mapdl.solve()

    mapdl.finish()

    # Post Processing
    mapdl.post1()
    mapdl.set(1)

    # print("# NUMERIC: ")
    # print("## Stresses: ")

    _, _, failures = anaylse_stackup(mapdl, shaft.get_stackup())

    # print("## Failures: ")
    # print(failures)

    max_failure = get_relevant_value(failures)

    # mapdl.post_processing.plot_element_displacement("Z")
    # mapdl.post_processing.plot_nodal_component_stress('z')
    return max_failure  # safety
