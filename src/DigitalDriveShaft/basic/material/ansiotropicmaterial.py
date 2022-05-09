from .material import Material, Mapdl, ndarray, np


class AnsiotropicMaterial(Material):
    def __init__(self,
                 stiffness: ndarray,
                 density: float, **kwargs):
        self.stiffness = stiffness
        super().__init__(dict(DENS=density), **kwargs)

    def get_stiffness(self) -> ndarray:
        return self.stiffness

    def get_compliance(self) -> ndarray:
        return np.linalg.inv(self.get_stiffness())

    def add_to_mapdl(self, mapdl: Mapdl, mat_id: int):
        # TB, Lab, MATID, NTEMP, NPTS, TBOPT, --, FuncName
        # TBDATA,,
        mapdl.tb("ANEL", mat_id, "", "", 0)
        mapdl.tbtemp(0)
        mapdl.tbdata("",
                     self.stiffness[0, 0],
                     self.stiffness[0, 1],
                     self.stiffness[0, 2],
                     self.stiffness[0, 3],
                     self.stiffness[0, 4],
                     self.stiffness[0, 5])
        mapdl.tbdata("",
                     self.stiffness[1, 1],
                     self.stiffness[1, 2],
                     self.stiffness[1, 3],
                     self.stiffness[1, 4],
                     self.stiffness[1, 5],
                     self.stiffness[2, 2])
        mapdl.tbdata("",
                     self.stiffness[2, 3],
                     self.stiffness[2, 4],
                     self.stiffness[2, 5],
                     self.stiffness[3, 3],
                     self.stiffness[3, 4],
                     self.stiffness[3, 5])
        mapdl.tbdata("",
                     self.stiffness[4, 4],
                     self.stiffness[4, 5],
                     self.stiffness[5, 5])
        mapdl.mpdata("DENS", mat_id, "", self.attr.get("DENS"))
