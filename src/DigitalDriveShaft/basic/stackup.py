from typing import List, Optional
import numpy as np
from .ply import Ply


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
    
    def calc_density(self):
        raise NotImplemented # TODO: @Willi bitte implementieren
        

    def rotate(self, angle) -> "Stackup":
        plies = [0]*len(self.plies)
        for i in range(len(self.plies)):
            plies[i] = self.plies[i].rotate(angle)

        return Stackup(plies)

    def get_abd(self, truncate=True):
        if self.abd is None:
            # Calculate the total thickness.
            h = self.thickness / 2

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
    
    def get_Nu12(self):
        """
        Wir brauchen die Querkontraktionszahl des Laminats

        Raises
        ------
        NotImplemented
            DESCRIPTION.

        Returns
        -------
        None.

        """
        raise NotImplemented        # TODO: @Willi: bitte implementieren. Wird bei calc_Buckling benötigt
        
    def get_Nu21(self):
        E_1 = self.get_abd[0, 0] / self.calc_thickness()  
        E_2 = self.get_abd[1, 1] / self.calc_thickness()
        Nu21 = self.get_Nu12()*E_2/E_1
        return Nu21

    def apply_load(self, mech_load: np.ndarray) -> np.ndarray:
        """
        Calculate the strain and curvature of the full plate under a given load using Kirchhoff plate theory.
        Parameters
        ----------
        mech_load : vector
            The load vector consits of are :math:`(N_x, N_y, N_{xy}, M_x, M_y, M_{xy})^T`
        Returns
        -------
        deformation : vector
            This deformation consists of :math:`(\varepsilon_x, \varepsilon_y
            \varepsilon_{xy},\kappa_x, \kappa_y, \kappa_{xy})^T`
        """
        return np.ravel(np.linalg.inv(self.get_abd()).dot(mech_load))

    def apply_deformation(self, deformation: np.ndarray) -> np.ndarray:
        r"""
        Calculate the running load and moment of the plate under a given using Kichhoff plate theory.
        Parameters
        ----------
        deformation : vector
            This deformation consists of :math:`(\varepsilon_x, \varepsilon_y,
            \varepsilon_{xy},\kappa_x, \kappa_y, \kappa_{xy})^T`
        Returns
        -------
        load : vector
            The load vector consits of are :math:`(N_x, N_y, N_{xy}, M_x, M_y, M_{xy})^T`
        """
        return np.ravel(self.get_abd().dot(deformation))

    def get_strains(self, deformation: np.ndarray):  # TODO: TEST it!
        # Calculating total thickness of the layup.
        h = self.thickness / 2

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
            strain_ply = [strain_lt_bot, strain_lt_top]
            strains.append(strain_ply)
            z_bot = z_top

        return strains

    def get_stresses(self, strains):  # TODO: TEST it!
        # Create a list for the stresses in each ply.
        stresses = []

        # Iterate over all plies.
        for i in range(len(self.plies)):
            # Obtain the strains from this ply.
            strain_lt_bot = strains[i][0]
            strain_lt_top = strains[i][1]

            # Convert strains into stresses.
            Q = self.plies[i].get_stiffness()
            stress_lt_top = Q.dot(strain_lt_top)
            stress_lt_bot = Q.dot(strain_lt_bot)

            # Store the stress values of this ply.
            stress_ply = [stress_lt_bot, stress_lt_top]
            stresses.append(stress_ply)

        return stresses

    def is_safe(self, stresses):
        for i in range(len(stresses)):
            ply_stress = stresses[i]
            material = self.plies[i].get_material()
            if not material.is_safe(stresses=ply_stress):
                return False
        return True

