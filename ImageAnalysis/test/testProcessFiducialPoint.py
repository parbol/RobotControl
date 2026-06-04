import ImageAnalysis.ProcessFiducialPoint as ProcessFiducialPoint



if __name__=='__main__':

    p = ProcessFiducialPoint.ProcessFiducialPoint('picture_X397.893Y-101.071Z128.5.png', is_ETROC=False)
    x, y, valid = p.fit()
    p = ProcessFiducialPoint.ProcessFiducialPoint('ETROC_1AX_-282.810Y_-347.920Z_158.671RZ_114.610J1_-96.744J2_-90.305J3_158.671J4_72.439.png', True)
    x, y, valid = p.fit()
    p = ProcessFiducialPoint.ProcessFiducialPoint('ETROC_1AX_-282.810Y_-367.140Z_158.635RZ_114.610J1_-96.503J2_-85.984J3_158.635J4_67.877.png', True)
    x, y, valid = p.fit()


