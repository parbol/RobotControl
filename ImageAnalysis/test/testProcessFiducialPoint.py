import ImageAnalysis.ProcessFiducialPoint as ProcessFiducialPoint




if __name__=='__main__':

    p = ProcessFiducialPoint.ProcessFiducialPoint('picture.png')
    x, y, d, valid = p.fit()


