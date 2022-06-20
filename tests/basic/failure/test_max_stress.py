import pytest
from src.DigitalDriveShaft.basic.failure import *


@pytest.mark.parametrize("init_args, exception_msg", [
    (([1.0, 1.0, ], ), "Stress-Strength Tensor has to be size 3 or 6! (Got: 2)")
])
def test_init_exceptions(init_args, exception_msg):
    with pytest.raises(ValueError) as exc_info:
        MaxStressFailure(*init_args)
    exception_raised = exc_info.value
    assert exception_raised.args[0] == exception_msg


@pytest.mark.parametrize("init_args, stresses, exception_msg", [
    (([1.0, 1.0, 1.0],), None, "Need stress tensor in Voigt notation!"),
    (([1.0, 1.0, 1.0],), [1.0], "Stresses has to be of length 3 (2d stress), but got length 1."),
    (([1.0, 1.0, 1.0],), [1.0, 2.0], "Stresses has to be of length 3 (2d stress), but got length 2."),
    (([1.0, 1.0, 1.0, 1.0, 1.0, 1.0],), [1.0], "Stresses has to be of length 6 (3d stress), but got length 1.")
])
def test_get_failure_exceptions(init_args, stresses, exception_msg):
    failure = MaxStressFailure(*init_args)
    with pytest.raises(ValueError) as exc_info:
        failure.get_failure(stresses)
    exception_raised = exc_info.value
    assert exception_raised.args[0] == exception_msg


@pytest.fixture
def maxstress2d():
    yield MaxStressFailure([1.0, 1.0, 1.0])


@pytest.mark.parametrize("stress, safety", [
    ([0.0, 0.0, 0.0], 0.0),
    ([1.0, 0.0, 0.0], 1.0),
    ([1.0, 0.0, 1.0], 1.0),
    ([1.0, 1.0, 1.0], 1.0),
    ([1.2, 1.0, 1.0], 1.2),
    ([-1.2, 1.0, 1.0], 1.2),
])
def test_2d_failure(maxstress2d, stress, safety):
    result = maxstress2d.get_failure(stress)
    assert result == {"max_stress": safety}


@pytest.fixture
def maxstress3d():
    yield MaxStressFailure([1.0, 1.0, 1.0, 0.5, 0.5, 0.5])


@pytest.mark.parametrize("stress, safety", [
    ([0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 0.0),
])
def test_3d_failure(maxstress3d, stress, safety):
    result = maxstress3d.get_failure(stress)
    assert result == {"max_stress": safety}


