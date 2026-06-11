import ImageAnalysis.ProcessFiducialPoint as ProcessFiducialPoint



if __name__=='__main__':

    p = ProcessFiducialPoint.ProcessFiducialPoint('FiducialMark/PCB_1X_405.230Y_-334.680Z_174.212RZ_107.110J1_-14.900J2_-65.989J3_174.212J4_-26.222.png', is_ETROC=False)
    x, y, valid = p.fit()
