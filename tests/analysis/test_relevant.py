import pytest
from src.DigitalDriveShaft.analysis import calc_static_porperties, get_relevant_value


@pytest.mark.parametrize(
    "values, compr, result",
    [
        ([0.0, [1, 2, 3], [4, 5, 6]], max, 6),
        ([0.0, [1, 2, 3], [4, 5, 6]], min, 0),
        ([{"max-stress": 2.0}, [{"max-stress": 1.0}, {"max-stress": 0.0}]], max, 2.0),
        ([{"max-stress": 2.0}, [{"max-stress": 1.0}, {"max-stress": 0.0}]], min, 0.0),
    ]
)
def test_get_relevant_value(values, compr, result):
    sol = get_relevant_value(values, compr)
    assert sol == result
