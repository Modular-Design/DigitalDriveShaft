import numpy as np
from .material import Material


class Ply:
    def __init__(self,
                 material: Material,
                 thickness: float,
                 rotation=0.0, degree=False):
        """
        Ply or Lamina

        Parameters
        ----------
        material : Material
            material of the ply
        thickness : float
            thickness of the ply
        rotation : float, optional
            rotation of the ply in [rad] or [deg] when degree is set True
        degree : bool, optional
            changes the measurement system of rotation, default is False

        References
        ----------
        .. [1] J. Ashton and J.M. Whitney, "Theory of Laminated Plates",
           Technomic, vol. 4, 1970
        """
        self.material = material
        self.thickness = thickness
        if degree:
            rotation = rotation * np.pi / 180.0
        self.rotation = rotation
        compl = self.material.get_plane_strain_stiffness()
        self.plane_strain = self.material.get_plane_strain_stiffness()

    def rotate(self, rad, degree=False) -> "Ply":
        """
        Rotate Ply

        Parameters
        ----------
        angle
            angle in [rad] or [deg] when degree is set True
        degree : bool, optional
            changes the measurement system of angle, default is False

        Returns
        -------
        Stackup
            new instance of the rotated Stackup

        Examples
        --------

        >>> ply = Ply(material, 1.0, 0.0)
        >>> rot_ply = ply.rotate(90, degree=True)
        Be aware, that the ply is left untouched.
        To change this, use:
        >>> ply = ply.rotate(90, degree=True)
        instead.
        """
        if degree:
            rad = rad * np.pi / 180.0
        return Ply(self.material, self.thickness, self.rotation + rad)

    def get_stiffness(self) -> np.ndarray:
        c = np.cos(self.rotation)
        s = np.sin(self.rotation)
        t_sigma = np.array([[c ** 2, s ** 2, - 2 * s * c],
                            [s ** 2, c ** 2, 2 * s * c],
                            [s * c, - s * c, c ** 2 - s ** 2]])

        t_sigmat = np.array([[c ** 2, s ** 2, s * c],
                             [s ** 2, c ** 2, -s * c],
                             [-2 * s * c, 2 * s * c, c ** 2 - s ** 2]])
        stiffness_rot = np.matmul(t_sigma, np.matmul(self.plane_strain, t_sigmat))
        return stiffness_rot

    def get_material(self) -> Material:
        """
        Material of the ply

        Returns
        -------
        Material
            Material of the ply.
        """
        return self.material

    def get_thickness(self) -> float:
        """
        Thickness of the ply

        Returns
        -------
        float
            Thickness of the ply.
        """
        return self.thickness

    def get_rotation(self, degree=False) -> float:
        """
        Rotation of the ply.

        Parameters
        ----------
        degree : bool, optional
            changes the measurement system of the return value, default is False

        Returns
        -------
        float:
            Rotation angle of the ply.
            By default the Unit is in [rad], but can be [deg] if degree is set to True.
        """
        if degree:
            return self.rotation * 180.0 / np.pi
        return self.rotation

    def get_local_stress(self, stress: np.ndarray) -> np.ndarray:
        """
        Stress in ply coordinate system.
        Parameters
        ----------
        stress : array
            stress tensor in Voigt notation / [sig_11, sig_22, sig_12]

        Returns
        -------
        array
            2d stress tensor in Voigt notation
        """
        angle = self.rotation  # TODO: Maybe -self.rotation
        m = np.cos(angle)
        n = np.sin(angle)
        T1_inv = np.array([[m ** 2, n ** 2, 2 * m * n],
                           [n ** 2, m ** 2, -2 * m * n],
                           [-m * n, m * n, m ** 2 - n ** 2]])
        return np.ravel(T1_inv.dot(stress))

    def get_local_strain(self, strain: np.ndarray) -> np.ndarray:
        """
        Strain in ply coordinate system.
        Parameters
        ----------
        strain : array
            strain tensor in Voigt notation / [eps_11, eps_22, gamma_12]

        Returns
        -------
        array
            2d strain tensor in Voigt notation
        """
        angle = self.rotation  # TODO: Maybe -self.rotation
        m = np.cos(angle)
        n = np.sin(angle)
        T2_inv = np.array([[m ** 2, n ** 2, m * n],
                           [n ** 2, m ** 2, -m * n],
                           [-2 * m * n, 2 * m * n, m ** 2 - n ** 2]])
        return np.ravel(T2_inv.dot(strain))
