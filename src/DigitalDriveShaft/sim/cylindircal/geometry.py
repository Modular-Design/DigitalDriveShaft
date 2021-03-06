from typing import Optional, Union, Literal
from ansys.mapdl.core import Mapdl
from src.DigitalDriveShaft.cylindrical import DriveShaft
from ..elements import Shell181, Solid185
from ..material import material_to_mapdl
from .mesh import CylindricMeshBuilder
import numpy as np


def driveshaft_to_mapdl(mapdl: Mapdl, shaft: DriveShaft,
                        element_type=Union[Literal["SHELL"], Literal["SOLID"]],
                        mesh_builder: Optional[dict] = None
                        ):
    mapdl.csys(1)

    if mesh_builder is None:
        mesh_builder = {}

    mesh_builder = CylindricMeshBuilder(**mesh_builder)

    if element_type is None:
        element_type = "SHELL"

    if element_type == "SHELL":
        __mesh_with_shell__(mapdl, shaft, mesh_builder)
    elif element_type == "SOLID":
        raise NotImplementedError("SOLID is not fully supported yet.")
        # __mesh_with_solid__(mapdl, shaft, mesh_builder)


def __mesh_with_shell__(mapdl: Mapdl,
                        shaft: DriveShaft,
                        mesh_builder: CylindricMeshBuilder):
    start_id = 1
    dz = shaft.form.length() / mesh_builder.n_z
    dphi = (mesh_builder.phi_max - mesh_builder.phi_min) / mesh_builder.n_phi
    zs = np.arange(shaft.form.min_z(), shaft.form.max_z() + dz, dz)
    phis = np.arange(mesh_builder.phi_min, mesh_builder.phi_max + dphi, dphi)
    k_start = start_id
    k_id = k_start
    for phi in phis:
        for z in zs:
            r = shaft.get_center_radius(z, phi, False)
            mapdl.k(k_id, r, phi / np.pi * 180, z)
            k_id += 1
    k_end = k_id - 1
    # mapdl.kplot()
    z_divs = len(zs) - 1
    phi_divs = len(phis) - 1
    combinations = z_divs * phi_divs
    rel_positions = [0] * combinations
    # areas first in z-direction then in phi
    index = 0
    for i in range(phi_divs):
        for j in range(z_divs):
            # counter clockwise
            rel_positions[index] = ((j + (j + 1)) / (2 * len(zs)), (phis[i] + phis[i + 1]) / 2)
            index += 1
            """
            d - c
            |   |
            a - b
            """
            a = i * (z_divs + 1) + j + 1
            b = (i + 1) * (z_divs + 1) + j + 1
            c = (i + 1) * (z_divs + 1) + j + 2
            d = i * (z_divs + 1) + j + 2
            mapdl.a(a, b, c, d)
    element = Shell181(1)
    element.set_integration(2)
    element.set_layer_storage(1)
    element.add_to_mapdl(mapdl)
    material_hashes = []
    for i in range(combinations):
        z, phi = rel_positions[i]
        laminat = shaft.stackup.get_value(z, phi)
        plies = laminat.get_plies()
        sec_id = i + 1
        mapdl.sectype(secid=sec_id, type_="SHELL", name="shell181")
        for ply in plies:
            material = ply.get_material()
            mat_hash = hash(material)
            if mat_hash in material_hashes:
                mat_id = material_hashes.index(mat_hash) + 1
            else:
                mat_id = len(material_hashes) + 1
                material_hashes.append(mat_hash)
                material_to_mapdl(mapdl, material, mat_id)

            mapdl.secdata(ply.get_thickness(), mat_id, ply.get_rotation(degree=True) + 90, 3)
        mapdl.asel("S", "AREA", '', i + 1)
        mapdl.esize(0, 1)
        mapdl.type(1)
        mapdl.secnum(sec_id)
        mapdl.amesh("ALL")


def __mesh_with_solid__(mapdl: Mapdl,
                        shaft: DriveShaft,
                        mesh_builder: CylindricMeshBuilder
                        ):
    start_id = 1
    dz = shaft.form.length() / mesh_builder.n_z
    dphi = (mesh_builder.phi_max - mesh_builder.phi_min) / mesh_builder.n_phi
    zs = np.arange(shaft.form.min_z(), shaft.form.max_z() + dz, dz)
    phis = np.arange(mesh_builder.phi_min, mesh_builder.phi_max + dphi, dphi)
    k_start = start_id
    k_id = k_start
    n_plies = len(shaft.stackup.get_value(0, 0).get_plies())
    for phi in phis:
        for z in zs:
            laminat = shaft.stackup.get_value(z, phi, iso=False)
            plies = laminat.get_plies()
            r = shaft.get_inner_radius(z, phi, iso=False)
            mapdl.k(k_id, r, phi / np.pi * 180, z)
            k_id += 1
            for ply in plies:
                r += ply.get_thickness()
                mapdl.k(k_id, r, phi / np.pi * 180, z)
                k_id += 1
    k_end = k_id - 1
    # mapdl.kplot(show_bounds=True, show_keypoint_numbering=True)
    n_phis = len(phis)
    n_zs = len(zs)
    z_offset = n_plies + 1
    phi_offset = n_zs * z_offset
    v_id = 1
    mapdl.et(1, "SOLID186")
    # mapdl.smrtsize("OFF")
    for j in range(n_phis - 1):
        for i in range(n_zs - 1):
            """
            d - c
            |   |
            a - b
            """
            a = j * phi_offset + i * z_offset
            b = (j + 1) * phi_offset + i * z_offset
            c = (j + 1) * phi_offset + (i + 1) * z_offset
            d = j * phi_offset + (i + 1) * z_offset
            z_mid = (zs[i] + zs[i + 1]) / 2.0
            phi_mid = (phis[j] + phis[j + 1]) / 2.0
            laminat = shaft.stackup.get_value(z_mid, phi_mid, False)
            plies = laminat.get_plies()
            shaft.stackup.get_value(0, 0).get_plies()
            for p in range(n_plies):
                """
                top:
                p8 - p7
                |    |
                p5 - p6
                
                bottom 
                p4 - p3
                |    |
                p1 - p2
                """
                p1 = a + p + 1
                p2 = b + p + 1
                p3 = c + p + 1
                p4 = d + p + 1
                p5 = a + p + 2
                p6 = b + p + 2
                p7 = c + p + 2
                p8 = d + p + 2
                mapdl.v(p1, p2, p3, p4, p5, p6, p7, p8)
                # if v_id > 10:
                #     print(v_id)
                #     mapdl.vsel("S", "VOLU", '', "ALL")
                #     mapdl.vplot()
                mapdl.vsel("S", "VOLU", '', v_id)
                mapdl.esize(0, 1)
                mapdl.mat(plies[p].get_material().get_id())
                mapdl.vmesh("ALL")
                mapdl.local(v_id, 1, 0, 0, 0, plies[p].get_rotation() / np.pi * 180.0 + 90)
                mapdl.esel("S", "ELEM", "", v_id)
                mapdl.emodif("all", "ESYS", v_id)
                v_id += 1
    k_end = k_id - 1
    mapdl.vsel("S", "VOLU", '', "ALL")
    mapdl.esel("S", "ELEM", "", "ALL")