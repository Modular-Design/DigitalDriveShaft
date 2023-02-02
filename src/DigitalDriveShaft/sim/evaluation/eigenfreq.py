import math

from src.DigitalDriveShaft.cylindrical import DriveShaft
from src.DigitalDriveShaft.basic import Loading
from src.DigitalDriveShaft.analysis import get_relevant_value
from ..cylindrical import driveshaft_to_mapdl, anaylse_stackup
from ansys.mapdl.core import Mapdl
from typing import Optional, List
import numpy as np
from ..cylindrical import CylindricMeshBuilder


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
    #
    # mapdl.csys(1)
    # mapdl.omega("", "", 1e1)  # [Hz]
    # Fixation
    # """
    """
    mapdl.nsel("S", "LOC", "Z", 0)
    mapdl.d("ALL", "UX", 0)
    mapdl.d("ALL", "UY", 0)
    mapdl.d("ALL", "UZ", 0)
    mapdl.nsel("ALL")

    length = shaft.get_length()
    mapdl.nsel("S", "LOC", "Z", length)
    # mapdl.d("ALL", "UX", 0)
    mapdl.d("ALL", "ALL", 0)
    mapdl.allsel("ALL")
    mapdl.cm("SHAFT", "ELEM")
    # 
    
    # Solver no rotation
    mapdl.slashsolu()
    mapdl.antype(antype="MODAL")
    mapdl.modopt(method="LANB", nmode=3)
    mapdl.mxpand(4)
    mapdl.solve()
    result = mapdl.result
    f0 = result.time_values
    mapdl.finish()
    
    return (f0).tolist()  # eigen-frequencies in [RPM?]
    """

    output = mapdl.modal_analysis(nmode=10, freqb=1)
    result = mapdl.result
    # print(result.time_values)
    # print(output)
    return list(result.time_values)

