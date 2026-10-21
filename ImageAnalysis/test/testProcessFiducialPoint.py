import ImageAnalysis.ProcessFiducialPoint as ProcessFiducialPoint



if __name__=='__main__':

    # p = ProcessFiducialPoint.ProcessFiducialPoint('../ETROC_1AX_-264.240Y_-369.240Z_158.558RZ_114.610J1_-93.689J2_-88.693J3_158.558J4_67.772.png', True)
    # x, y, valid = p.fit(th=55)
    p = ProcessFiducialPoint.ProcessFiducialPoint('../PCB_1X_404.630Y_-376.750Z_172.546RZ_107.110J1_-22.030J2_-55.365J3_172.546J4_-29.715.png', False)
    x, y, valid = p.fit(th=150)
    p = ProcessFiducialPoint.ProcessFiducialPoint('../PCB_1X_404.630Y_-376.750Z_172.567RZ_107.110J1_-22.030J2_-55.365J3_172.567J4_-29.715.png', False)
    x, y, valid = p.fit(th=150)
