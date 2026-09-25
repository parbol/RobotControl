import ImageAnalysis.ProcessFiducialPoint as ProcessFiducialPoint



if __name__=='__main__':

    p = ProcessFiducialPoint.ProcessFiducialPoint('../PCB_1X_351.260Y_-376.750Z_172.444RZ_107.110J1_-21.096J2_-69.686J3_172.444J4_-16.329.png', False)
    x, y, valid = p.fit(th=150)
