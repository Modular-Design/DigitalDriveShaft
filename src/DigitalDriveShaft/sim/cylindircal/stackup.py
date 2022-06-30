from typing import Optional
from ansys.mapdl.core import Mapdl
from src.DigitalDriveShaft.cylindrical import CylindricalStackup
import numpy as np


def anaylse_stackup(mapdl: Mapdl,
                    stackup: CylindricalStackup,
                    calculate_failures=True,
                    id_offset: Optional[int] = 0):

    phis = mapdl.post_processing.element_values('CENT', 'Y')
    zs = mapdl.post_processing.element_values('CENT', 'Z')
    mapdl.rsys('LSYS')
    stresses = []
    strains = []
    failures = []

    for elem_id in range(len(zs)):
        phi_pos, z_pos = phis[elem_id], zs[elem_id]
        mapdl.esel("S", "ELEM", '', elem_id)
        current_stackup = stackup.get_laminat(z_pos, phi_pos, iso=False)
        no_layers = len(current_stackup.get_plies())
        layer_stress = []
        layer_strain = []
        for i in range(no_layers):
            mapdl.layer(i + 1)

            mapdl.shell('bot')

            sigma_x = mapdl.post_processing.element_stress('X')[0]
            sigma_y = mapdl.post_processing.element_stress('Y')[0]
            sigma_xy = mapdl.post_processing.element_stress('XY')[0]
            bot_stress = [sigma_x, sigma_y, sigma_xy]

            epes_x = mapdl.post_processing.element_values('EPEL', 'X')[0]
            epes_y = mapdl.post_processing.element_values('EPEL', 'Y')[0]
            epes_xy = mapdl.post_processing.element_values('EPEL', 'XY')[0]
            bot_strain = [epes_x, epes_y, epes_xy]

            # assert round(sx_max, sign_bot) == round(sol_bot, sign_bot)

            mapdl.shell('top')
            sigma_x = mapdl.post_processing.element_stress('X')[0]
            sigma_y = mapdl.post_processing.element_stress('Y')[0]
            sigma_xy = mapdl.post_processing.element_stress('XY')[0]
            top_stress = [sigma_x, sigma_y, sigma_xy]

            epes_x = mapdl.post_processing.element_values('EPEL', 'X')[0]
            epes_y = mapdl.post_processing.element_values('EPEL', 'Y')[0]
            epes_xy = mapdl.post_processing.element_values('EPEL', 'XY')[0]
            top_strain = [epes_x, epes_y, epes_xy]

            layer_stress.append((bot_stress, top_stress))
            layer_strain.append((bot_strain, top_strain))

        if calculate_failures:
            failures.append(current_stackup.get_failure(layer_stress, layer_strain))
        stresses.append(layer_stress)
        strains.append(layer_strain)

    mapdl.rsys(0)
    return stresses, strains, failures


def extract_stackup_stresses(mapdl: Mapdl,
                                    stackup: CylindricalStackup,
                                    id_offset: Optional[int] = 0):
    mapdl.rsys('LSYS')
    stresses = []

    no_layers = len(stackup.get_laminat(0.0, 0.0, iso=False).get_plies())

    for i in range(no_layers):
        mapdl.layer(i + 1)
        mapdl.shell('bot')
        sigma_x = mapdl.post_processing.element_stress('X')
        sigma_y = mapdl.post_processing.element_stress('Y')
        sigma_xy = mapdl.post_processing.element_stress('XY')
        bot_stress = (sigma_x, sigma_y, sigma_xy)
        # assert round(sx_max, sign_bot) == round(sol_bot, sign_bot)
        mapdl.shell('top')
        sigma_x = mapdl.post_processing.element_stress('X')
        sigma_y = mapdl.post_processing.element_stress('Y')
        sigma_xy = mapdl.post_processing.element_stress('XY')
        top_stress = (sigma_x, sigma_y, sigma_xy)
        stresses.append((bot_stress, top_stress))

    mapdl.rsys(0)
    return stresses
