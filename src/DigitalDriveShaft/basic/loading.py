from pydantic import BaseModel
from typing import List
from typing import Optional


class Vector(BaseModel):
    x = 0.0
    y = 0.0
    z = 0.0

    def as_list(self) -> List[float]:
        return [self.x, self.y, self.z]


class Loading(BaseModel):
    fx: Optional[float] = 0 #N
    fy: Optional[float] = 0 #N
    fz: Optional[float] = 0 #N
    mx: Optional[float] = 0 #Nm
    my: Optional[float] = 0 #Nm
    mz: Optional[float] = 0 #Nm
    rpm: Optional[float] = 0 #U/min
