from DigitalDriveShaft.cylindrical import DriveShaft
from ..cylindrical import driveshaft_to_mapdl
from ansys.mapdl.core import Mapdl
from typing import Optional, List
import numpy as np
import math


def calc_bending(
    mapdl: Mapdl, shaft: DriveShaft, mesh_builder: Optional[dict] = None
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
        mapdl.clear()
        mapdl.prep7()
        driveshaft_to_mapdl(
            mapdl, shaft, element_type="SHELL", mesh_builder=mesh_builder
        )
        mapdl.asel("ALL")
        mapdl.nummrg("NODE")

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
    length = shaft.get_length()
    mapdl.nsel("S", "LOC", "Z", length)
    nodes = mapdl.mesh.nodes

    # radius = shaft.get_center_radius(length, 0, False)

    fx_i = 1.0 / len(nodes)
    fy_i = 0.0 / len(nodes)
    for node in nodes:
        x = node[0]
        y = node[1]
        phi_rad = math.atan2(y, x)
        phi_deg = phi_rad / np.pi * 180
        mapdl.nsel("S", "LOC", "Z", length)
        mapdl.nsel("R", "LOC", "Y", phi_deg)
        mapdl.csys(0)  # INFO: it seems like FCs are always in csys(0), maybe skip this
        mapdl.f("ALL", "FX", fx_i)
        mapdl.f("ALL", "FY", fy_i)
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
