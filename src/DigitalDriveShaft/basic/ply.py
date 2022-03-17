import numpy as np
from .materials import Material, get_plane_stress_stiffness



class Ply:
    def __init__(self, material: Material, thickness: float, rotation=0.0):
        self.material = material
        self.thickness = thickness
        self.rotation = rotation
        self.plane_stress = get_plane_stress_stiffness(self.material)

    def rotate(self, angle) -> "Ply":
        angle = angle * np.pi / 180  # convert to radians
        return Ply(self.material, self.thickness, self.rotation + angle)

    def get_stiffness(self):
        m = np.cos(self.rotation)
        n = np.sin(self.rotation)
        T1 = np.matrix([[m ** 2, n ** 2, 2 * m * n],
                        [n ** 2, m ** 2, -2 * m * n],
                        [-m * n, m * n, m ** 2 - n ** 2]])
        T2 = np.matrix([[m ** 2, n ** 2, m * n],
                        [n ** 2, m ** 2, -m * n],
                        [-2 * m * n, 2 * m * n, m ** 2 - n ** 2]])
        stiffness_rot = np.linalg.inv(T1) * self.plane_stress * T2
        return stiffness_rot

    def get_material(self):
        return self.material

    def get_local_stress(self, stress):
        angle = self.rotation  # TODO: Maby -self.rotation
        m = np.cos(angle)
        n = np.sin(angle)
        T1_inv = np.matrix([[m ** 2, n ** 2, 2 * m * n],
                            [n ** 2, m ** 2, -2 * m * n],
                            [-m * n, m * n, m ** 2 - n ** 2]])
        stress_rot = T1_inv * stress
        return np.ravel(stress_rot)

    def get_local_strain(self, strain):
        angle = self.rotation  # TODO: Maby -self.rotation
        m = np.cos(angle)
        n = np.sin(angle)
        T2_inv = np.matrix([[m ** 2, n ** 2, m * n],
                            [n ** 2, m ** 2, -m * n],
                            [-2 * m * n, 2 * m * n, m ** 2 - n ** 2]])
        return np.ravel(T2_inv.dot(strain))
