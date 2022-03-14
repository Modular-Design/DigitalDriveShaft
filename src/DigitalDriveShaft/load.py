from pydantic import BaseModel
from typing import List


class Vector(BaseModel):
    x = 0.0
    y = 0.0
    z = 0.0

    def as_list(self) -> List[float]:
        return [self.x, self.y, self.z]


