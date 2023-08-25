from DigitalDriveShaft.cylindrical import DriveShaft
from DigitalDriveShaft.analysis import Loading
from ..cylindrical import driveshaft_to_mapdl
from ansys.mapdl.core import Mapdl
from typing import Optional, List
import numpy as np


def calc_deformation(
    mapdl: Mapdl, shaft: DriveShaft, load: Loading, mesh_builder: Optional[dict] = None
) -> List[float]:
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
        driveshaft_to_mapdl(
            mapdl, shaft, element_type="SHELL", mesh_builder=mesh_builder
        )
        mapdl.asel("ALL")
        mapdl.nummrg("NODE")

    # master RBE3
    offset = 0
    if mesh_builder is not None:
        exts = mesh_builder.get("extensions")
        if exts is not None:
            offset = exts[1]
    length = shaft.get_length() + offset
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

    mapdl.csys(0)
    # Loading
    mapdl.cmsel("S", "master")
    mapdl.f("ALL", "FX", load.fx)
    mapdl.f("ALL", "FY", load.fy)
    mapdl.f("ALL", "FZ", load.fz)
    mapdl.f("ALL", "MZ", load.mz)

    mapdl.csys(1)

    mapdl.nsel("ALL")

    # Solver
    mapdl.antype("STATIC")
    mapdl.outres("ALL", "ALL")
    mapdl.solve()

    mapdl.finish()

    # Post Processing
    mapdl.post1()
    mapdl.set(1)

    # access results using MAPDL object
    u_max = mapdl.post_processing.element_displacement("NORM", "MAX")

    return np.max(u_max)
