from pymaterial.materials import Material
from pymaterial.failures import IFailure
from ansys.mapdl.core import Mapdl
from .failure import failure_to_mapdl


def material_to_mapdl(mapdl: Mapdl, material: Material, mat_id: int):
    """
    Converts the material to an anisotropic MAPDL material.

    Parameters
    ----------
    mapdl: Mapdl
        Mapdl object (``from ansys.mapdl.core import Mapdl``)
        where the material should be added

    material: Material
    mat_id

    Returns
    -------


    Examples
    --------

    >>> from ansys.mapdl.core import launch_mapdl
    >>> from src.DigitalDriveShaft.basic import IsotropicMaterial
    >>> mapdl = launch_mapdl(mode="grpc", loglevel="ERROR")
    >>> material = IsotropicMaterial()
    >>> material_to_mapdl(mapdl, material, 1)
    """

    stiffness = material.get_stiffness()
    # TB, Lab, MATID, NTEMP, NPTS, TBOPT, --, FuncName
    # TBDATA,,
    mapdl.tb("ANEL", mat_id, "", "", 0)
    # mapdl.mptemp(mat_id, 0)
    mapdl.tbtemp(0)
    mapdl.tbdata(
        "",
        stiffness[0, 0],
        stiffness[0, 1],
        stiffness[0, 2],
        stiffness[0, 3],
        stiffness[0, 4],
        stiffness[0, 5],
    )
    mapdl.tbdata(
        "",
        stiffness[1, 1],
        stiffness[1, 2],
        stiffness[1, 3],
        stiffness[1, 4],
        stiffness[1, 5],
        stiffness[2, 2],
    )
    mapdl.tbdata(
        "",
        stiffness[2, 3],
        stiffness[2, 4],
        stiffness[2, 5],
        stiffness[3, 3],
        stiffness[3, 4],
        stiffness[3, 5],
    )
    mapdl.tbdata("", stiffness[4, 4], stiffness[4, 5], stiffness[5, 5])

    density = material.get_density()
    if density is not None:
        # mapdl.mpdata("DENS", mat_id, "", density)
        mapdl.mp("DENS", mat_id, density)
    else:
        raise ValueError("Density is None.")

    failures = material.get_failures()
    for failure in failures:
        if not isinstance(failure, IFailure):
            continue
        failure_to_mapdl(mapdl, failure, mat_id)
