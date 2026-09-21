import ImageAnalysis.ProcessCalibrationPoint as ProcessCalibrationPoint
import os
import pickle
import sys
from matplotlib import pyplot as plt
import numpy as np



#################################################################
if __name__=='__main__':


    #This directory must exist to store the fits
    #fitOutput = './fitsNoddingTest/'
    fitOutput = '/home/pablo/Documentos/softwareProjects/RobotControl/ImageAnalysis/test/Pictures/Fits-Quick-Check/'
    #listDir contains the name of the directory for a give set of pictures
    #and the threshold to be applied in the pattern reconition
    # listDir.append(['./newCalibrations/calibrationDataPoints3', 30])
    # listDir.append(['./newCalibrations/Final_Calibration3', 100])
    # listDir.append(['/home/antonio/Escritorio/ModuleAssembly/ETL/Final_Calibration4/pictures', 100])
    dirname = '/home/pablo/Documentos/softwareProjects/RobotControl/ImageAnalysis/test/Pictures/Quick-Check/'
    
    #dirname = '/home/pablo/Documentos/softwareProjects/RobotControl/ImageAnalysis/test/Pictures/NoddingTest'
    threshold = 30
    rep = open('report.txt', 'w')
    for i in os.listdir(dirname):
        name = dirname + '/' + i
        p = ProcessCalibrationPoint.ProcessCalibrationPoint(name, fitOutput)
        x, y, r, valid = p.fit(threshold)
        cad = f'Processed {name} with center: ({x}, {y}) and radius {r}\n'
        rep.write(cad)
    rep.close()


        

        



