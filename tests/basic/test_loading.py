from src.DigitalDriveShaft.basic import Vector


def test_as_list():
    vec = Vector()
    vec.x = 1.0
    liste = vec.as_list()
    assert len(liste) == 3
    assert liste[0] == 1.0
    assert liste[1] == 0.0
    assert liste[2] == 0.0