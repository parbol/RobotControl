import ImageAnalysis.ProcessFiducialPoint as ProcessFiducialPoint



if __name__=='__main__':

    # p = ProcessFiducialPoint.ProcessFiducialPoint('picture_X397.893Y-101.071Z128.5.png', is_ETROC=False)
    # x, y, valid = p.fit()
    p = ProcessFiducialPoint.ProcessFiducialPoint('FiducialMark/ETROC_1AX_-262.940Y_-367.130Z_158.535RZ_114.600J1_-93.508J2_-89.396J3_158.535J4_68.304.png', True)
    x, y, valid = p.fit()
    # p = ProcessFiducialPoint.ProcessFiducialPoint('ETROC_1AX_-282.810Y_-367.140Z_158.635RZ_114.610J1_-96.503J2_-85.984J3_158.635J4_67.877.png', True)
    # x, y, valid = p.fit()


