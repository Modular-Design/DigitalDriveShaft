from ansys.mapdl.core import Mapdl
from .element import Element


class Shell181(Element):
    def __init__(self, element_id: int):
        super().__init__(element_id, "SHELL181")
        self.secdata = list()

    def set_element_fitness(self, value: int):
        """
        Element stiffness:
            0 -- Bending and membrane stiffness (default)
            1 -- Membrane stiffness only
            2 -- Stress/strain evaluation only
        """
        self.options[1] = value

    def set_integration(self, value: int):
        """
        Integration option:
            0 -- Reduced integration with hourglass control (default)
            2 -- Full integration with incompatible modes
        """
        self.options[3] = value

    def set_normal_orientation(self, value: int):
        """
        Shell normal orientation option:
            0 -- Calculated from element connectivity (default)
            1 -- Controlled by the z coordinate direction of a local coordinate system
        """
        self.options[4] = value

    def set_shell_formulation(self, value: int):
        """
        Curved shell formulation:
            0 -- Standard shell formulation (default)
            1 -- Advanced curved-shell formation
            2 -- Simplified curved-shell formation
        """
        self.options[5] = value

    def set_layer_storage(self, value: int):
        """
        Specify layer data storage:
            0 -- For multi-layer elements, store data for bottom of bottom layer
                    and top of top layer. For single-layer elements, store data for TOP and BOTTOM.
                    (Default)
            1 -- Store data for TOP and BOTTOM, for all layers (multi-layer elements)
            2 -- Store data for TOP, BOTTOM, and MID for all layers; applies to single- and multi-layer elements
        """
        self.options[8] = value

    def set_thickness_option(self, value: int):
        """
        User thickness option:
            0 -- No user subroutine to provide initial thickness (default)
            1 -- Read initial thickness data from user-defined subroutine UTHICK
        """
        self.options[9] = value

    def set_normal_stress(self, value: int):
        """
        Thickness normal stress (Sz) output option:
            0 -- Sz not modified (default, Sz = 0)
            1 -- Recover and output Sz from applied pressure load
        """
        self.options[10] = value

    def set_axis_orientation(self, value: int):
        """
        Default element x axis (x0) orientation:
            0 -- First parametric direction at the element centroid (default)
            1 -- Pointing from element node I to element node J
        """
        self.options[11] = value

    def add_layer(self, thickness: float, mat_id: int, rotation: float, integration_points: int):
        self.secdata.append([thickness, mat_id, rotation, integration_points])

    def add_to_mapdl(self, mapdl: Mapdl):
        super().add_to_mapdl(mapdl)

        mapdl.sectype(self.element_id, "SHELL")
        for data in self.secdata:
            mapdl.secdata(data[0], data[1], data[2], data[3])
