import ImageAnalysis.ProcessCalibrationPoint as ProcessCalibrationPoint




if __name__=='__main__':

    p = ProcessCalibrationPoint.ProcessCalibrationPoint('picture.png')
    x, y, valid = p.fit()


