from src.DigitalDriveShaft.abd.abdcal import QPlaneStress


def test_qplanestress():
    q = QPlaneStress(141000, 9340, 0.350, 4500)
    # eLamX 2.6: default material (properties as above), angle=0, laminat: 1 layer, thickness=1
    sol = [[142153.51020354172, 3295.7434386906234, 0], [3295.7434386906234, 9416.409824830353, 0], [0, 0, 4500]]
    for i in range(len(sol)):
        for j in range(len(sol[i])):
            assert round(q[i][j], 3) == round(sol[i][j], 3)
