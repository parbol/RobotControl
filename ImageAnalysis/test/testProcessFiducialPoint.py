import ImageAnalysis.ProcessFiducialPoint as ProcessFiducialPoint



if __name__=='__main__':

    p = ProcessFiducialPoint.ProcessFiducialPoint('../FiducialETROCs_2026-9-21-10/ETROC_1AX_-283.810Y_-366.740Z_158.693RZ_114.610J1_-96.657J2_-85.898J3_158.693J4_67.945.png', True)
    x, y, valid = p.fit()
