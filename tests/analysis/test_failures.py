import pytest
from src.DigitalDriveShaft.basic.failure import *


@pytest.fixture
def stressfailure():
    return MaxStressFailure([1.0, 1.0, 1.0])


@pytest.mark.parametrize("stress, safety", [
    ([0.0, 0.0, 0.0], 0.0),
    ([1.0, 0.0, 0.0], 1.0),
    ([1.0, 0.0, 1.0], 1.0),
    ([1.0, 1.0, 1.0], 1.0),
    ([1.2, 1.0, 1.0], 1.2),
    ([-1.2, 1.0, 1.0], 1.2),
])
def test_failure(stressfailure, stress, safety):
    result = stressfailure.get_failure(stress)
    assert result == {"max_stress": safety}
