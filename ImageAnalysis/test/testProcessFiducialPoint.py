import ImageAnalysis.ProcessFiducialPoint as ProcessFiducialPoint



if __name__=='__main__':

    p = ProcessFiducialPoint.ProcessFiducialPoint('../FiducialETROCs_2026-9-21-17/FiducialETROCs/ETROC_1BX_-249.840Y_-350.420Z_158.545RZ_114.610J1_-91.757J2_-95.280J3_158.545J4_72.427.png', True)
    x, y, valid = p.fit(th=35)
