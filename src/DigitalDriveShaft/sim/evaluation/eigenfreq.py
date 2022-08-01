import math

from src.DigitalDriveShaft.cylindrical import DriveShaft
from src.DigitalDriveShaft.basic import Loading
from src.DigitalDriveShaft.analysis import get_relevant_value
from ..cylindircal import driveshaft_to_mapdl, anaylse_stackup
from ansys.mapdl.core import Mapdl
from typing import Optional, List
import numpy as np
from ..cylindircal import CylindricMeshBuilder


def calc_eigenfreq(mapdl: Mapdl, shaft: DriveShaft, mesh_builder: Optional[dict] = None) -> List[float]:
    """

    Parameters
    ----------
    mapdl
    shaft
    load
    mesh_builder: dict
        dictionary might containing: "n_z", "phi_max", "phi_min" (both in [DEG]), "n_phi"

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
    mapdl.slashsolu()
    mapdl.csys(1)
    mapdl.omega("", "", 1)  # [Hz]
    # Fixation

    mapdl.nsel("S", "LOC", "Z", 0)
    mapdl.d("ALL", "UX", 0)
    mapdl.d("ALL", "UY", 0)
    mapdl.d("ALL", "UZ", 0)

    length = shaft.get_length()
    mapdl.nsel("S", "LOC", "Z", length)
    mapdl.d("ALL", "UX", 0)
    mapdl.d("ALL", "UZ", 0)
    mapdl.nsel("ALL")

    # Solver
    mapdl.antype(antype="MODAL")
    mapdl.modopt(method="LANB", nmode="10", freqb="1.")
    # mapdl.wrfull(ldstep="1")
    mapdl.solve()
    mapdl.finish()

    mapdl.post1()

    result = mapdl.result
    f = result.time_values

    return f.tolist()  # eigen-frequencies in [Hz]
