from src.DigitalDriveShaft.basic import TransverselyIsotropicMaterial, Stackup, Ply, CuntzeFailure
from src.DigitalDriveShaft.cylindrical import SimpleDriveShaft
from src.DigitalDriveShaft.analysis import get_relevant_value
import numpy as np
from src.DigitalDriveShaft.sim.cylindircal import anaylse_stackup, driveshaft_to_mapdl
import pytest
from ansys.mapdl.core import launch_mapdl


composite_failure = CuntzeFailure(141000.0, 2200, 1850, 55, -200, 120)

composite = TransverselyIsotropicMaterial(E_l=141000.0, E_t=9340.0,  # N/mm^2
                                          nu_lt=0.35,
                                          G_lt=4500.0, density=1.7E-6, # kg/mm^3
                                          failures=[composite_failure])

mapdl = launch_mapdl(mode="grpc", loglevel="ERROR")

def test_stackup():
    length = 40  # 10  # 1000  # mm
    r_inner = 5.0  # 5  # 30 # mm
    n_z = 10  # 30
    n_phi = 16  # 10
    phi_max = np.pi
    phi_min = -np.pi
    ply0 = Ply(material=composite,
               thickness=0.5)
    stackup = Stackup([ply0])
    # cyl_stackup = CylindricalStackup(lambda z, phi: stackup)
    shaft = SimpleDriveShaft(r_inner * 2.0, length, stackup)
    # init mapdl
    mapdl.finish()
    mapdl.clear()
    mapdl.prep7()
    # Mesh
    # material_to_mapdl(mapdl, composite, 1)
    driveshaft_to_mapdl(mapdl, shaft, n_z=n_z, phi_max=phi_max, phi_min=phi_min, n_phi=n_phi, element_type='SHELL')
    mapdl.asel("ALL")
    # BC
    mapdl.nummrg("NODE")
    mapdl.run("/solu")
    mapdl.nsel("S", "LOC", "Z", 0)
    mapdl.d("ALL", "UX", 0)
    mapdl.d("ALL", "UY", 0)
    mapdl.d("ALL", "UZ", 0)
    mapdl.nsel("ALL")
    radius = shaft.get_center_radius(length, 0, False)
    mapdl.lsel("S", "LOC", "Z", length)
    mapdl.sfl("ALL", "PRES", - 1 / (2 * np.pi * radius))
    mapdl.nsel("ALL")
    # solver config
    mapdl.antype("STATIC")
    mapdl.outres("ALL", "ALL")
    mapdl.solve()
    mapdl.finish()
    # Post Processing
    mapdl.post1()
    mapdl.set(1)
    stresses, strains, failures = anaylse_stackup(mapdl, shaft.get_stackup(), calculate_failures=False)
    max_stress = get_relevant_value(stresses)
    mapdl.post_processing.plot_nodal_component_stress('z')
    # max_failure = get_relevant_value(failures)
    print(stresses)
    print(max_stress)
    # print(max_failure)
    # mapdl.exit()
    # assert False


if __name__ == "__main__":
    test_stackup()
    mapdl.exit()
    # mapdl.post_processing.plot_nodal_component_stress('x')
