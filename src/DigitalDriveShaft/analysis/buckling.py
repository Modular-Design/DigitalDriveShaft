from ..cylindrical import DriveShaft
from ..basic import Loading
import numpy as np


def calc_crit_moment(shaft: DriveShaft):
    (_, stackup) = shaft.get_value(0.5, 0.0)
    laminate_thickness = stackup.calc_thickness()
    d_shaft_outer = 2 * shaft.get_outer_radius(0.5, 0.0)

    k_s = 0.925  # Beiwert für gelenkige Lagerung
    k_l = 0.77  # Beiwert für Imperfektionsanfälligkeit
    homogenization = stackup.calc_homogenized()
    em_axial = homogenization.get_E1()  # MPa # E Modul der Verbundschicht
    em_circ = homogenization.get_E2()  # MPa
    nu_12 = homogenization.get_nu12()  # Querkontraktionszahl der Verbundschicht
    nu_21 = homogenization.get_nu21()

    result = k_s * k_l * np.pi ** 3 / 6
    result *= (d_shaft_outer / 2) ** (5 / 4)
    result *= laminate_thickness ** (9 / 4) / np.sqrt(shaft.get_length())
    result *= em_axial ** (3 / 8)
    result *= (em_circ / (1 - nu_12 * nu_21)) ** (5 / 8) / 1000
    return result


def calc_moment_safety(shaft: DriveShaft, load: Loading):
    mz_buckling = calc_crit_moment(shaft)
    safety_buckling = mz_buckling / load.mz
    return safety_buckling
