from .imapdlfailure import IMAPDLFailure, Mapdl
from typing import Optional


class MAPDLFailure(IMAPDLFailure):
    def __init__(self,
                 stress_attr: Optional[dict] = None,
                 strain_attr: Optional[dict] = None,
                 temperature_attr: Optional[dict] = None,
                 ):
        if stress_attr is None:
            stress_attr = dict()
        self.stress_attr = stress_attr

        if strain_attr is None:
            strain_attr = dict()
        self.strain_attr = strain_attr

        if temperature_attr is None:
            temperature_attr = dict()
        self.temperature_attr = temperature_attr

    def add_to_mapdl(self, mapdl: Mapdl, mat_id: int):
        for (key, value) in self.stress_attr.items():
            mapdl.fc(mat_id,  "S", key, value)

        for (key, value) in self.strain_attr.items():
            mapdl.fc(mat_id,  "TEMP", key, value)

        for (key, value) in self.temperature_attr.items():
            mapdl.fc(mat_id,  "EPEL", key, value)
