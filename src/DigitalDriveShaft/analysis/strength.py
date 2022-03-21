from ..cylindrical import DriveShaft
from ..basic import Loading
import numpy as np


def calc_strength(shaft: DriveShaft, load: Loading):
    (shaft_radius, stackup) = shaft.get_value_in_iso_scale(0.5, 0.5)
    laminate_thickness = stackup.get_thickness()
    d_shaft_inner = 2*shaft_radius
    A_shaft = np.pi/4*(d_shaft_inner**2-(d_shaft_inner + 2 * laminate_thickness)**2) #Cross section of shaft
    d_center_stackup = 2 * shaft_radius + (0.5 - shaft.get_contour_factor()) * laminate_thickness
    circ_shaft = np.pi * d_center_stackup

    nx = load.fx/circ_shaft    #N/mm
    ny = 0                  #N/mm   
    nxy = load.mx/1000/(d_center_stackup/2/circ_shaft) + np.sqrt((load.fy)**2 + (load.fz)**2)/A_shaft*laminate_thickness  #N/mm 
    mx = 0                  #N      
    my = np.sqrt((load.my/1000/d_center_stackup/2)**2 + (load.mz/1000/d_center_stackup/2)**2)     #N
    mxy = 0                         

    mech_load = np.array([nx, ny, nxy, mx, my, mxy])
    deformation = stackup.apply_load(mech_load)
    strains = stackup.get_strains(deformation)
    stresses = stackup.get_stresses(strains)
    return stackup.is_safe(stresses)



def calc_buckling(shaft: DriveShaft, load: Loading):
    (shaft_radius, stackup) = shaft.get_value_in_iso_scale(0.5, 0.5)
    laminate_thickness = stackup.calc_thickness()
    d_shaft_outer = 2 * shaft_radius + 2 * (0.5 - shaft.get_contour_factor()) * laminate_thickness
    
    k_s = 0.925  # Beiwert für gelenkige Lagerung
    k_l = 0.77  # Beiwert für Imperfektionsanfälligkeit
    E_axial = stackup.get_abd[0, 0] / laminate_thickness  # MPa #20000 bei Sebastian
    E_circ = stackup.get_abd[1, 1] / laminate_thickness  # MPa #20000 bei Sebastian
    
    m_buckling = k_s * k_l * np.pi ** 3 / 6 * (d_shaft_outer / 2) ** (5 / 4) * laminate_thickness ** (9 / 4) / np.sqrt(
        shaft_length) * E_axial ** (3 / 8) * (E_circ / (1 - stackup.get_Nu12() * stackup.get_Nu21())) ** (5 / 8) / 1000
    safety_buckling = m_buckling / load.mx
    
    
    return safety_buckling


def calc_dynamicStability(shaft: DriveShaft, load: Loading):
    (shaft_radius, stackup) = shaft.get_value_in_iso_scale(0.5, 0.5)
    laminate_thickness = stackup.calc_thickness()
    d_shaft_outer = 2 * shaft_radius + 2 * (0.5 - shaft.get_contour_factor()) * laminate_thickness
    
    
    E_axial = stackup.get_abd[0, 0] / laminate_thickness  # MPa #20000 bei Sebastian
    
    # Formel für Berechnung von Biegekritischer Drehzahl aus Sebastians Excel
    RPM_crit = 60 / 2 * np.pi / np.sqrt(8) * d_shaft_outer / shaft_length ** 2 * np.sqrt(
        1000 ** 3 * E_axial / (stackup.calc_density()))  # u/min
    safety_RPM_crit = RPM_crit / load.rpm
    return safety_RPM_crit
