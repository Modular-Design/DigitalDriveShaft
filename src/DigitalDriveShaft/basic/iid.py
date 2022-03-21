from abc import ABC

from ansys.mapdl.core import Mapdl


class IID:
    def set_id(self, id: int):
        raise NotImplementedError()

    def get_id(self) -> float:
        raise NotImplementedError()


class IIDMAPDL(IID, ABC):
    def add_to_mapdl(self, mapdl: Mapdl, id: int):
        raise NotImplementedError()
