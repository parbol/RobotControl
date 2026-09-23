import ImageAnalysis.ProcessFiducialPoint as ProcessFiducialPoint



if __name__=='__main__':

    p = ProcessFiducialPoint.ProcessFiducialPoint('../ETROC_1BX_-230.440Y_-350.420Z_158.397RZ_114.610J1_-88.833J2_-98.228J3_158.397J4_72.451.png', True)
    x, y, valid = p.fit(th=40)
