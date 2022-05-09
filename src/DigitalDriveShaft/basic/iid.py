from abc import ABC

from .mapdl import Mapdl


class IID:
    def set_id(self, id: int):
        raise NotImplementedError()

    def get_id(self) -> float:
        raise NotImplementedError()


class IMAPDL(ABC):
    def add_to_mapdl(self, mapdl: Mapdl, **kwargs):
        raise NotImplementedError()
