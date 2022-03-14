from typing import List
import numpy as np


class Ply:
    def __init__(self, stiffness, thickness: float, rotation=0.0, alpha=None):
        self.stiffness = stiffness
        self.thickness = thickness
        self.rotation = rotation

    def rotate(self, angle) -> "Ply":
        angle = angle * np.pi / 180  # convert to radians
        m = np.cos(angle)
        n = np.sin(angle)
        T1 = np.matrix([[m ** 2, n ** 2, 2 * m * n],
                        [n ** 2, m ** 2, -2 * m * n],
                        [-m * n, m * n, m ** 2 - n ** 2]])
        T2 = np.matrix([[m ** 2, n ** 2, m * n],
                        [n ** 2, m ** 2, -m * n],
                        [-2 * m * n, 2 * m * n, m ** 2 - n ** 2]])
        stiffness_rot = np.linalg.inv(T1) * self.stiffness * T2
        return Ply(stiffness_rot, self.thickness, self.rotation + angle)

    def get_stiffness(self):
        return self.stiffness

    def get_local_stress(self, stress):
        angle = self.rotation  # TODO: Maby -self.rotation
        m = np.cos(angle)
        n = np.sin(angle)
        T1_inv = np.matrix([[m ** 2, n ** 2, 2 * m * n],
                            [n ** 2, m ** 2, -2 * m * n],
                            [-m * n, m * n, m ** 2 - n ** 2]])
        stress_rot = T1_inv * stress
        return stress_rot

    def get_local_strain(self, strain):
        angle = self.rotation  # TODO: Maby -self.rotation
        m = np.cos(angle)
        n = np.sin(angle)
        T2_inv = np.matrix([[m ** 2, n ** 2, m * n],
                            [n ** 2, m ** 2, -m * n],
                            [-2 * m * n, 2 * m * n, m ** 2 - n ** 2]])
        return T2_inv * strain



class Stackup:
    def __init__(self, plies: List[Ply], thickness=None):
        self.plies = plies
        if thickness is None:
            thickness = self.calc_thickness()
        self.thickness = thickness
        self.abd = None

    def calc_thickness(self) -> float:
        thickness = 0.0
        for ply in self.plies:
            thickness = thickness + ply.thickness
        return thickness

    def rotate(self, angle) -> "Stackup":
        plies = [0]*len(self.plies)
        for i in range(len(self.plies)):
            plies[i] = self.plies[i].rotate(angle)

        return Stackup(plies)

    def get_abd(self, truncate=True):
        if self.abd is None:
            # Calculate the total thickness.
            h = sum(self.thickness) / 2

            # Create empty matricces for A B en D.
            A = np.zeros((3, 3))
            B = np.zeros((3, 3))
            D = np.zeros((3, 3))

            # Loop over all plies
            z_bot = -h
            for ply in self.plies:
                # Calculate the z coordinates of the top and bottom of the ply.
                z_top = z_bot + ply.thickness

                # Rotate the local stiffenss matrix.
                Q_bar = ply.get_stiffness()

                # Calculate the contribution to the A, B and D matrix of this layer.
                Ai = Q_bar * (z_bot - z_top)
                Bi = 1 / 2 * Q_bar * (z_bot ** 2 - z_top ** 2)
                Di = 1 / 3 * Q_bar * (z_bot ** 3 - z_top ** 3)

                # Summ this layer to the previous ones.
                A = A + Ai
                B = B + Bi
                D = D + Di
                z_bot = z_top

            # Compile the entirety of the ABD matrix.
            self.abd = np.matrix([[A[0, 0], A[0, 1], A[0, 2], B[0, 0], B[0, 1], B[0, 2]],
                             [A[1, 0], A[1, 1], A[1, 2], B[1, 0], B[1, 1], B[1, 2]],
                             [A[2, 0], A[2, 1], A[2, 2], B[2, 0], B[2, 1], B[2, 2]],
                             [B[0, 0], B[0, 1], B[0, 2], D[0, 0], D[0, 1], D[0, 2]],
                             [B[1, 0], B[1, 1], B[1, 2], D[1, 0], D[1, 1], D[1, 2]],
                             [B[2, 0], B[2, 1], B[2, 2], D[2, 0], D[2, 1], D[2, 2]]])

        # Truncate very small values.
        if truncate is True:
            return np.matrix(np.where(np.abs(self.abd) < np.max(self.abd) * 1e-6, 0, self.abd))
        return self.abd

    def apply_load(self, mech_load: List[float]):
        return np.inv(self.get_abd()).dot(mech_load)

    def apply_deformation(self, deformation: List[float]):
        return self.get_abd().dot(deformation)

    def get_strains(self, deformation: List[float]):  # TODO: TEST it!
        # Calculating total thickness of the layup.
        h = sum(self.thickness) / 2

        # Calculate deformation of the midplane of the laminate.
        strain_membrane = deformation[:3]
        curvature = deformation[3:]

        # Create a list for the strains in each ply.
        strains = []
        z_bot = -h

        # Iterate over all plies.
        for ply in self.plies:
            # Calculate the z coordinates of the top and bottom of the ply.
            z_top = z_bot + ply.thickness

            # Caluclate strain in the ply.
            strain_top = strain_membrane + z_top * curvature
            strain_bot = strain_membrane + z_bot * curvature

            # Rotate strain from global to ply axis sytstem.
            strain_lt_top = ply.get_local_strain(strain_top)
            strain_lt_bot = ply.get_local_strain(strain_bot)

            # Store the strain values of this ply.
            strain_ply = [strain_lt_top, strain_lt_bot]
            strains.append(strain_ply)
            z_bot = z_top

        return strains

    def get_stresses(self, strains):  # TODO: TEST it!
        # Create a list for the stresses in each ply.
        stresses = []

        # Iterate over all plies.
        for i in range(len(self.plies)):
            # Obtain the strains from this ply.
            strain_lt_top = strains[i][0]
            strain_lt_bot = strains[i][1]

            # Convert strains into stresses.
            Q = self.plies[i].get_stiffness()
            stress_lt_top = Q.dot(strain_lt_top)
            stress_lt_bot = Q.dot(strain_lt_bot)

            # Store the stress values of this ply.
            stress_ply = [stress_lt_top, stress_lt_bot]
            stresses.append(stress_ply)

        return stresses
