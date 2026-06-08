import ImageAnalysis.ProcessFiducialPoint as ProcessFiducialPoint



if __name__=='__main__':

    p = ProcessFiducialPoint.ProcessFiducialPoint('FiducialMark/ETROC_1AX_-262.940Y_-347.930Z_158.545RZ_114.610J1_-93.770J2_-93.712J3_158.545J4_72.871.png', is_ETROC=False)
    x, y, valid = p.fit()
    p = ProcessFiducialPoint.ProcessFiducialPoint('FiducialMark/ETROC_1AX_-262.940Y_-367.130Z_158.533RZ_114.600J1_-93.508J2_-89.396J3_158.533J4_68.304.png', is_ETROC=False)
    x, y, valid = p.fit()
    p = ProcessFiducialPoint.ProcessFiducialPoint('FiducialMark/ETROC_1AX_-282.810Y_-347.920Z_158.667RZ_114.610J1_-96.744J2_-90.305J3_158.667J4_72.439.png', is_ETROC=False)
    x, y, valid = p.fit()
    p = ProcessFiducialPoint.ProcessFiducialPoint('FiducialMark/ETROC_1AX_-282.810Y_-367.140Z_158.642RZ_114.610J1_-96.503J2_-85.984J3_158.642J4_67.877.png', is_ETROC=False)
    x, y, valid = p.fit()
    p = ProcessFiducialPoint.ProcessFiducialPoint('FiducialMark/PCB_1X_353.350Y_-374.330Z_173.659RZ_107.040J1_-20.703J2_-69.801J3_173.659J4_-16.536.png', is_ETROC=False)
    x, y, valid = p.fit()
    p = ProcessFiducialPoint.ProcessFiducialPoint('FiducialMark/PCB_1X_353.630Y_-335.130Z_173.846RZ_107.020J1_-14.563J2_-78.820J3_173.846J4_-13.637.png', is_ETROC=False)
    x, y, valid = p.fit()
    p = ProcessFiducialPoint.ProcessFiducialPoint('FiducialMark/PCB_1X_406.730Y_-375.120Z_173.849RZ_107.030J1_-21.824J2_-55.182J3_173.849J4_-30.024.png', is_ETROC=False)
    x, y, valid = p.fit()
    p = ProcessFiducialPoint.ProcessFiducialPoint('FiducialMark/PCB_1X_407.120Y_-335.970Z_174.160RZ_107.050J1_-15.162J2_-65.160J3_174.160J4_-26.728.png', is_ETROC=False)
    x, y, valid = p.fit()
    # p = ProcessFiducialPoint.ProcessFiducialPoint('FiducialMark/ETROC_1AX_-262.940Y_-347.930Z_158.547RZ_114.610J1_-93.770J2_-93.712J3_158.547J4_72.871.png', True)
    # x, y, valid = p.fit()
    # p = ProcessFiducialPoint.ProcessFiducialPoint('ETROC_1AX_-282.810Y_-367.140Z_158.635RZ_114.610J1_-96.503J2_-85.984J3_158.635J4_67.877.png', True)
    # x, y, valid = p.fit()


