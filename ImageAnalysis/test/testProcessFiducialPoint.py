import ImageAnalysis.ProcessFiducialPoint as ProcessFiducialPoint



if __name__=='__main__':

    p = ProcessFiducialPoint.ProcessFiducialPoint('../ETROC_1AX_-264.240Y_-350.420Z_158.612RZ_114.610J1_-93.917J2_-92.949J3_158.612J4_72.256.png', True)
    x, y, valid = p.fit(th=100)
