from ..mapdl import Mapdl


class IMAPDLFailure:
    def add_to_mapdl(self, mapdl: Mapdl, mat_id: int):
        raise NotImplementedError
