import math

from src.DigitalDriveShaft.cylindrical import DriveShaft
from src.DigitalDriveShaft.basic import Loading
from src.DigitalDriveShaft.analysis import get_relevant_value
from ..cylindircal import driveshaft_to_mapdl, anaylse_stackup
from ansys.mapdl.core import Mapdl
from typing import Optional
import numpy as np
from ..cylindircal import CylindricMeshBuilder


def calc_strength(mapdl: Mapdl, shaft: DriveShaft, load: Loading, mesh_builder: Optional[dict] = None) -> float:
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
    fx_i = load.fx / len(nodes)
    fy_i = load.fy / len(nodes)
    fz_i = load.fz / len(nodes)
    mz_i = load.mz / len(nodes)
    for node in nodes:
        x = node[0]
        y = node[1]
        radius = math.sqrt(x ** 2 + y ** 2)
        fm_i = mz_i / radius
        phi_rad = math.atan2(y, x)
        phi_deg = phi_rad / np.pi * 180
        mapdl.nsel("S", "LOC", "Z", length)
        mapdl.nsel("R", "LOC", "Y", phi_deg)
        mapdl.csys(0)
        mapdl.f("ALL", "FX", fx_i - fm_i * math.sin(phi_rad))
        mapdl.f("ALL", "FY", fy_i + fm_i * math.cos(phi_rad))
        mapdl.f("ALL", "FZ", fz_i)
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

    stresses, strains, failures = anaylse_stackup(mapdl, shaft.get_stackup())
    max_failure = get_relevant_value(failures)

    # mapdl.post_processing.plot_nodal_component_stress('z')
    return 1 / max_failure  # safety