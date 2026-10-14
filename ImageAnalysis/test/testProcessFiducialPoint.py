import ImageAnalysis.ProcessFiducialPoint as ProcessFiducialPoint



if __name__=='__main__':

    p = ProcessFiducialPoint.ProcessFiducialPoint('../FiducialETROCs_2026-10-14-10/FiducialPCB/PCB_1X_404.830Y_-337.450Z_172.664RZ_107.110J1_-15.341J2_-65.459J3_172.664J4_-26.310.png', False)
    x, y, valid = p.fit(th=150)
