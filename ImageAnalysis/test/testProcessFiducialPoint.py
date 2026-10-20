import ImageAnalysis.ProcessFiducialPoint as ProcessFiducialPoint



if __name__=='__main__':

    p = ProcessFiducialPoint.ProcessFiducialPoint('../PCB_1X_404.630Y_-376.750Z_172.567RZ_107.110J1_-22.030J2_-55.365J3_172.567J4_-29.715.png', False)
    x, y, valid = p.fit(th=150)
