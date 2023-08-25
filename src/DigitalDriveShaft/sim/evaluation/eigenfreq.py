from DigitalDriveShaft.cylindrical import DriveShaft
from ..cylindrical import driveshaft_to_mapdl
from ansys.mapdl.core import Mapdl
from typing import Optional, List


def calc_eigenfreq(
    mapdl: Mapdl, shaft: DriveShaft, mesh_builder: Optional[dict] = None
) -> List[float]:
    """

    Parameters
    ----------
    mapdl
    shaft
    load
    mesh_builder: dict
        dictionary might containing:
            "n_z",
            "phi_max",
            "phi_min" (both in [DEG]),
            "n_phi"

    Returns
    -------
    min_safety
    """

    mapdl.finish()
    if mesh_builder is not None:
        mapdl.clear()
        mapdl.prep7()
        driveshaft_to_mapdl(
            mapdl, shaft, element_type="SHELL", mesh_builder=mesh_builder
        )
        mapdl.asel("ALL")
        mapdl.nummrg("NODE")

    # BCs
    #
    # mapdl.csys(1)
    # mapdl.omega("", "", 1e1)  # [Hz]
    # Fixation
    # """

    mapdl.csys(1)
    mapdl.nsel("S", "LOC", "Z", 0)
    mapdl.d("ALL", "UX", 0)
    mapdl.d("ALL", "UY", 0)
    mapdl.d("ALL", "UZ", 0)
    mapdl.nsel("ALL")

    length = shaft.get_length()
    mapdl.nsel("S", "LOC", "Z", length)
    mapdl.d("ALL", "UX", 0)
    mapdl.allsel("ALL")
    """
    mapdl.d("ALL", "ALL", 0)
    mapdl.allsel("ALL")
    mapdl.cm("SHAFT", "ELEM")
    #

    # Solver no rotation
    mapdl.slashsolu()
    mapdl.antype(antype="MODAL")
    mapdl.modopt(method="LANB", nmode=3)
    mapdl.mxpand(4)
    mapdl.solve()
    result = mapdl.result
    f0 = result.time_values
    mapdl.finish()

    return (f0).tolist()  # eigen-frequencies in [RPM?]
    """

    # result = mapdl.result
    # # print(result.time_values)
    # # print(output)
    # return list(result.time_values)
    r"""
    _output = mapdl.modal_analysis(nmode=10, freqb=1)
    mapdl.post1()
    resp = mapdl.set("LIST")
    w_n = np.array(re.findall(r"\s\d*\.\d\s", resp), np.float32)
    return w_n
    """

    # Modal Analysis
    mapdl.slashsolu()
    mm = mapdl.math
    nev = 10  # Get the first 10 modes
    _output = mapdl.modal_analysis("DAMP", nmode=nev)
    mapdl.finish()
    mm.free()

    k = mm.stiff(fname=f"{mapdl.jobname}.full")
    M = mm.mass(fname=f"{mapdl.jobname}.full")
    A = mm.mat(k.nrow, nev)
    eigenvalues = mm.eigs(nev, k, M, phi=A, fmin=1.0)
    return eigenvalues
