from ansys.mapdl.core import Mapdl


class Failure:
    def __init__(self, criteria:str, attr: dict):
        self.criteria = criteria
        self.attr = attr

    def add_to_mapdl(self, mapdl: Mapdl, mat_id: int):
        for (key, value) in self.attr.items():
            mapdl.fc(mat_id,  self.criteria, key, value)


class StressFailure(Failure):
    def __init__(self, attr: dict):
        super().__init__("S", attr)


class TempFailure(Failure):
    def __init__(self, attr: dict):
        super().__init__("TEMP", attr)


class StrainFailure(Failure):
    def __init__(self, attr: dict):
        super().__init__("EPEL", attr)


class OrthotropicStressFailure(StressFailure):
    def __init__(self,
                 tens_l: float, tens_t: float,
                 shear_lt: float, shear_tt: float,
                 compr_l: float, compr_t: float):
        super().__init__()