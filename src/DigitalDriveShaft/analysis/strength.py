from ..cylindrical import DriveShaft
from ..basic import Loading
import numpy as np


def calc_strength(shaft: DriveShaft, load: Loading):
    (shaft_radius, stackup) = shaft.get_value_in_iso_scale(0.5, 0.5)
    laminat_thickness = stackup.calc_thickness()
    d_center_stackup = 2 * shaft_radius + (0.5 - shaft.get_contour_factor()) * laminat_thickness
    u_shaft = np.pi * d_center_stackup

    nx = load.fx/u_shaft    #N/mm
    ny = 0                  #N/mm   
    nxy = load.mx/d_center_stackup/2/u_shaft     #N/mm # TODO: @Alrik bitte Formel ergänzen von Fy und Fz komponenten
    mx = 0                  #N      
    my = np.sqrt((load.my/1000/d_center_stackup/2)**2 + (load.mz/1000/d_center_stackup/2)**2)     #N
    mxy = 0                         

    mech_load = np.array([nx, ny, nxy, mx, my, mxy])
    deformation = stackup.apply_load(mech_load)
    strains = stackup.get_strains(deformation)
    stresses = stackup.get_stresses(strains)
    return stackup.is_safe(stresses)
