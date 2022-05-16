import numpy as np
from ansys.mapdl.core import Mapdl
from ..failure import IFailure, IMAPDLFailure
from ..iid import IMAPDL, IID
from typing import Optional, List, Union
from numpy import ndarray


class Material(IFailure, IMAPDL, IID):
    def __init__(self, attr: dict, failures: Optional[List[IFailure]] = None):
        """

        Parameters
        ----------
        attr : dict

        failures : List[IFailure], optional

        """
        self.id = 0
        self.attr = attr
        if failures is None:
            failures = []
        self.failures = failures

    def get_compliance(self) -> ndarray:
        raise NotImplementedError

    def get_stiffness(self) -> ndarray:
        return np.linalg.inv(self.get_compliance())

    def get_density(self) -> float:
        return self.attr.get("DENS")

    def get_failure(self,
                    stresses: Optional[Union[List[float], ndarray]] = None,
                    strains: Optional[Union[List[float], ndarray]] = None,
                    temperature: Optional[float] = None):
        """
        returns
        {"max_stress": 1.0, "cuntze": 0.5}
        """
        result = dict()
        for failure in self.failures:
            result.update(failure.get_failure(stresses, strains, temperature))
        return result

    def set_id(self, id: int):
        self.id = id

    def get_id(self) -> float:
        return self.id

    def get_plane_stress_stiffness(self):
        """
        Get stiffness tensor for plane stress
        Returns
        -------

        """
        elems = [0, 1, 5]  # ignore the s_zz, s_xy and s_yz row and column
        return self.get_stiffness()[elems][:, elems]

    def get_plane_strain_stiffness(self):
        """
        et stiffness tensor for plane strain
        Returns
        -------

        """
        elems = [0, 1, 5]  # ignore the s_zz, s_xy and s_yz row and column
        return np.linalg.inv(self.get_compliance()[elems][:, elems])

    def add_to_mapdl(self, mapdl: Mapdl, **kwargs):
        mat_id = kwargs.get("id")
        if mat_id is None and self.id is None:
            raise KeyError("'id' must be defined!")
        for (key, value) in self.attr.items():
            mapdl.mp(key, self.id, value)
        for failure in self.failures:
            if isinstance(failure, IMAPDLFailure):
                failure.add_to_mapdl(mapdl, mat_id)
