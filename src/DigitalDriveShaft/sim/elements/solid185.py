from .element import Element


class Solid185(Element):
    def __init__(self, element_id: int):
        super().__init__("SOLID185")

    def set_element_technology(self, value: int):
        """
        Element technology:
            0 -- Full integration with B method (default)
            1 -- Uniform reduced integration with hourglass control
            2 -- Enhanced strain formulation
            3 -- Simplified enhanced strain formulation
        """
        self.options[2] = value

    def set_layer_construction(self, value: int):
        """
        Layer construction:
            0 -- Structural Solid (default) -- nonlayered
            1 -- Layered Solid (not applicable to SOLID185 Structural Solid)
        """
        self.options[3] = value

    def set_element_formulation(self, value: int):
        """
        Element formulation:
            0 -- Use pure displacement formulation (default)
            1 -- Use mixed u-P formulation
        """
        self.options[6] = value

    def set_pml_absorbing_condition(self, value: int):
        """
        PML absorbing condition:
            0 -- Do not include PML absorbing condition (default)
            1 -- Include PML absorbing condition
        """
        self.options[15] = value

    def set_analysis_flag(self, value: int):
        """
        Steady-state analysis flag:
            0 -- Steady-state analysis disabled (default)
            1 -- Enable steady-state analysis
        """
        self.options[16] = value

    def set_surface_output(self, value: int):
        """
        Extra surface output:
            0 -- Basic element solution (default)
            4 -- Surface solution for faces with nonzero pressure
        """
        self.options[17] = value
