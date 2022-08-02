import math

from src.DigitalDriveShaft.cylindrical import DriveShaft
from ..cylindircal import driveshaft_to_mapdl, anaylse_stackup
from ansys.mapdl.core import Mapdl
from typing import Optional, List, Literal
import numpy as np
from ..cylindircal import CylindricMeshBuilder


def calc_buckling(mapdl: Mapdl, shaft: DriveShaft,
                  mesh_builder: Optional[dict] = None,
                  load_mode: Literal["FORCE", "MOMENT"] = "MOMENT") -> List[float]:
    """

    Parameters
    ----------
    mapdl
    shaft
    load
    mesh_builder: dict
        dictionary might containing: "n_z", "phi_max", "phi_min" (both in [DEG]), "n_phi"
    load_mode: str

    Returns
    -------
    min_safety
    """

    mapdl.finish()
    if mesh_builder is not None:
        mapdl.clear()
        mapdl.prep7()
        driveshaft_to_mapdl(
            mapdl, shaft,
            element_type='SHELL',
            mesh_builder=mesh_builder
        )
        mapdl.asel("ALL")
        mapdl.nummrg("NODE")

    # BCs
    mapdl.run("/solu")
    # Fixation
    mapdl.csys(1)
    mapdl.nsel("S", "LOC", "Z", 0)
    mapdl.d("ALL", "UX", 0)
    mapdl.d("ALL", "UY", 0)
    mapdl.d("ALL", "UZ", 0)
    mapdl.nsel("ALL")

    # Loading
    length = shaft.get_length()
    mapdl.nsel("S", "LOC", "Z", length)
    nodes = mapdl.mesh.nodes
    if load_mode == "FORCE":
        fz_i = 1.0 / len(nodes)
        mapdl.f("ALL", "FZ", fz_i)
    elif load_mode == "MOMENT":
        mz_i = 1.0 / len(nodes)
        for node in nodes:
            x = node[0]
            y = node[1]
            radius = math.sqrt(x ** 2 + y ** 2)
            fm_i = mz_i / radius
            phi_rad = math.atan2(y, x)
            phi_deg = phi_rad / np.pi * 180
            mapdl.nsel("S", "LOC", "Z", length)
            mapdl.nsel("R", "LOC", "Y", phi_deg)
            mapdl.csys(0)  # INFO: it seems like FCs are always in csys(0), so you might skip this
            mapdl.f("ALL", "FX", - fm_i * math.sin(phi_rad))
            mapdl.f("ALL", "FY", fm_i * math.cos(phi_rad))
            mapdl.csys(1)
    else:
        raise ValueError(f"load_mode is nether 'FORCE' or 'MOMENT'! (load_mode is: '{load_mode}')")
    mapdl.nsel("ALL")

    # source: https://homepage.tudelft.nl/p3r3s/bsc_projects/eindrapport_hogendoorn.pdf
    # compute linear  elastic
    mapdl.solve()
    mapdl.finish()

    # compute buckling
    mapdl.run("/solu")
    mapdl.pstres('ON')
    mapdl.antype("MODAL")
    mapdl.modopt("LANB", 1)
    mapdl.mxpand(20)
    mapdl.outres("ALL", "ALL")
    mapdl.solve()
    mapdl.finish()

    # mapdl.nsel("R", "LOC", "Y", 0)
    # mapdl.f("ALL", "FX", 0.01)  # imperfection

    # Post Processing
    mapdl.post1()

    result = mapdl.result
    eigen_val = result.time_values

    return eigen_val.tolist()  # safety