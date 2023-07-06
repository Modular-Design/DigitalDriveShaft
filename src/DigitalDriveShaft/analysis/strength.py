from ..cylindrical import DriveShaft
from .helpers import get_relevant_value, Loading, extract_failures
from typing import List, Tuple
import numpy as np


def calc_static_porperties(
    shaft: DriveShaft, load: Loading
) -> Tuple[
    List[Tuple[np.ndarray, np.ndarray]],
    List[Tuple[np.ndarray, np.ndarray]],
    List[Tuple[dict, dict]],
]:
    """computes the strains, stresses and failures of the driveshaft

    Parameters
    ----------
    shaft : DriveShaft
    load : Loading

    Returns
    -------
    list, list, list
        strains, stresses, failures
    """
    (_, stackup) = shaft.get_value(0.5, 0.0)
    laminate_thickness = stackup.calc_thickness()
    A_shaft = shaft.get_cross_section(0.5, 0.0)
    d_center_stackup = 2.0 * shaft.get_center_radius(0.5, 0.0)
    circ_shaft = np.pi * d_center_stackup

    nx = load.fz / circ_shaft  # N/mm
    ny = 0  # N/mm
    nxy = (
        load.mz / (d_center_stackup / 2 * circ_shaft)
        + np.sqrt((load.fy) ** 2 + (load.fx) ** 2) / A_shaft * laminate_thickness
    )  # N/mm
    mx = 0  # N
    my = np.sqrt(
        (load.my / d_center_stackup / 2) ** 2 + (load.mx / d_center_stackup / 2) ** 2
    )  # N
    mxy = 0

    mech_load = np.array([nx, ny, nxy, mx, my, mxy])
    deformation = stackup.apply_load(mech_load)
    strains = stackup.get_strains(deformation)
    stresses = stackup.get_stresses(
        strains
    )  # [(bot_0, top_0),(bot_1, top_1),...] with bot/top = [s_x, s_y, t_xy]
    failures = stackup.get_failure(stresses, strains)
    return strains, stresses, failures


def calc_strength(failures: List[Tuple[dict, dict]]) -> float:
    cuntze_failures = extract_failures(failures, ["cuntze"])
    max_loading = get_relevant_value(cuntze_failures)
    return max_loading
