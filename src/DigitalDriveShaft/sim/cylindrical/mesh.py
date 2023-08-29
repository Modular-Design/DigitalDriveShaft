from pydantic import BaseModel
from typing import Optional
import numpy as np


class CylindricMeshBuilder(BaseModel):
    n_z: Optional[int] = 10
    n_phi: Optional[int] = 16
    phi_max: Optional[float] = 2.0 * np.pi
    phi_min: Optional[float] = 0.0
    extensions: Optional[tuple] = (0, 0)
