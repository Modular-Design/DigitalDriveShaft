from ..cylindrical import DriveShaft
from .helpers import Loading
import numpy as np


def calc_crit_rpm(shaft: DriveShaft):
    (_, stackup) = shaft.get_value(0.5, 0.0)
    d_shaft_outer = 2 * shaft.get_outer_radius(0.5, 0.0)

    homogenization = stackup.calc_homogenized()
    em_axial = homogenization.get_E1()  # MPa # E Modul der Verbundschicht

    # Formel für Berechnung von Biegekritischer Drehzahl aus Sebastians Excel
    rpm_crit = (
        60
        / 2
        * np.pi
        / np.sqrt(8)
        * d_shaft_outer
        / shaft.get_length() ** 2
        * np.sqrt(1000**3 * em_axial / (stackup.calc_density()))
    )  # u/min
    return rpm_crit


def calc_rpm_safety(shaft: DriveShaft, load: Loading):
    rpm_crit = calc_crit_rpm(shaft)
    safety_rpm = rpm_crit / load.rpm
    return safety_rpm
