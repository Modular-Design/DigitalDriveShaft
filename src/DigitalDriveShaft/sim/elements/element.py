from ansys.mapdl.core import Mapdl


class Element:
    def __init__(self, element_id: int, element_name: str):
        self.element_id = element_id
        self.element_name = element_name
        self.options = dict()

    def add_to_mapdl(self, mapdl: Mapdl):
        mapdl.et(self.element_id, self.element_name)

        for key in self.options:
            value = self.options[key]
            mapdl.keyopt(self.element_id, key, value)

