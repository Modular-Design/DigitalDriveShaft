from ..cylindrical import DriveShaft
from ..basic import Loading
from typing import List, Union, Callable, Optional
import numpy as np


def get_relevant_value(values: list,
                       compr: Optional[Callable] = max) -> float:
    """
    Extrect the relevant value, by using a comparator.

    Parameters
    ----------
    values : list
        nested list, which somewhere include


    compr : func
        comperator function

    Returns
    -------
    float
        Relevant Failure value

    Examples
    --------

    You can use it for:

    - normal values and lists

       >>> values = [0.0, [1, 2, 3], [4, 5, 6]]
       Get the maximum value
       >>> get_relevant_value(values)
       Get the minimum value
       >>> get_relevant_value(values, compr=min)
       return 0.0

    - dicts

       >>> failures = [{"max-stress": 2.0}, [{"max-stress": 1.0}, {"max-stress": 0.0}]]
       Get the maximum failure value
       >>> get_relevant_value(failures)
       return 2.0
    """
    result = []
    for value in values:
        if isinstance(value, list):
            result += get_relevant_value(value, compr)
        elif isinstance(value, dict):
            result += dict(values).values()
        else:
            result.append(value)

    return compr(result)


def calc_strength(shaft: DriveShaft, load: Loading):
    (_, stackup) = shaft.get_value(0.5, 0.0)
    laminate_thickness = stackup.calc_thickness()
    A_shaft = shaft.get_Crosssection(0.5, 0.0)
    d_center_stackup = 2.0 * shaft.get_center_radius(0.5, 0.0)
    circ_shaft = np.pi * d_center_stackup

    nx = load.fx / circ_shaft  # N/mm
    ny = 0  # N/mm
    nxy = load.mx / 1000 / (d_center_stackup / 2 / circ_shaft) + np.sqrt(
        (load.fy) ** 2 + (load.fz) ** 2) / A_shaft * laminate_thickness  # N/mm
    mx = 0  # N
    my = np.sqrt((load.my / 1000 / d_center_stackup / 2) ** 2 + (load.mz / 1000 / d_center_stackup / 2) ** 2)  # N
    mxy = 0

    mech_load = np.array([nx, ny, nxy, mx, my, mxy])
    deformation = stackup.apply_load(mech_load)
    strains = stackup.get_strains(deformation)
    stresses = stackup.get_stresses(strains)  # [[bot_0, top_0],[bot_1, top_1],...] with bot/top = [s_x, s_y, t_xy]
    failures = stackup.get_failure(stresses)
    max_loading = get_relevant_value(failures)
    return max_loading


def calc_buckling(shaft: DriveShaft, load: Loading):
    (_, stackup) = shaft.get_value(0.5, 0.0)
    laminate_thickness = stackup.calc_thickness()
    d_shaft_outer = 2 * shaft.get_outer_radius(0.5, 0.0)
    
    k_s = 0.925     # Beiwert für gelenkige Lagerung
    k_l = 0.77      # Beiwert für Imperfektionsanfälligkeit
    homogenization = stackup.calc_homogenized()
    E_axial = homogenization.get_E1()   # MPa # E Modul der Verbundschicht #20000 bei Sebastian
    E_circ = homogenization.get_E2()    # MPa #20000 bei Sebastian
    Nu12 = homogenization.get_Nu12()    # Querkontraktionszahl der Verbundschicht
    Nu21 = homogenization.get_Nu21()
    
    m_buckling = k_s * k_l * np.pi ** 3 / 6 * (d_shaft_outer / 2) ** (5 / 4) * laminate_thickness ** (9 / 4) / np.sqrt(
        shaft.get_length()) * E_axial ** (3 / 8) * (E_circ / (1 - Nu12 * Nu21)) ** (5 / 8) / 1000
    safety_buckling = m_buckling / load.mx
    
    return safety_buckling


def calc_dynamic_stability(shaft: DriveShaft, load: Loading):
    (_, stackup) = shaft.get_value(0.5, 0.0)
    d_shaft_outer = 2 * shaft.get_outer_radius(0.5, 0.0)
    E_axial = stackup.get_E1            # MPa # E Modul der Verbundschicht #20000 bei Sebastian
    
    # Formel für Berechnung von Biegekritischer Drehzahl aus Sebastians Excel
    RPM_crit = 60 / 2 * np.pi / np.sqrt(8) * d_shaft_outer / shaft.get_length() ** 2 * np.sqrt(
        1000 ** 3 * E_axial / (stackup.calc_density()))  # u/min
    safety_RPM_crit = RPM_crit / load.rpm
    return safety_RPM_crit
