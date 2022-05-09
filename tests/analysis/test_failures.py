import pytest
from src.DigitalDriveShaft.basic.failure import *


@pytest.fixture
def planestressfailure():
    return PlaneMaxStressFailure(1.0, 1.0, 1.0, 1.0, -1.0, -1.0)


@pytest.mark.parametrize("stress, safety", [
    ([0.0, 0.0, 0.0], 0.0),
    ([1.0, 0.0, 0.0], 1.0),
    ([1.0, 0.0, 1.0], 1.0),
    ([1.0, 1.0, 1.0], 1.0),
    ([1.2, 1.0, 1.0], 1.2),
    ([-1.2, 1.0, 1.0], 1.2),
])
def test_failure(planestressfailure, stress, safety):
    result = planestressfailure.get_failure(stress)
    assert result == {"max_stress": safety}
