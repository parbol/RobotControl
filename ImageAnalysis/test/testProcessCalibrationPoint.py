import ImageAnalysis.ProcessCalibrationPoint as ProcessCalibrationPoint
import os
import pickle
import sys
from matplotlib import pyplot as plt
import numpy as np


#################################################################
def getAllNominalPoints():

    #Here we start from the bottom right 
    firstPointX = -132.0 
    firstPointY = -222.0 
    px = []
    py = []
    for ix in range(0, 23):
        for iy in range(0, 30):
            px.append(-132.0 + ix * 12.0)
            py.append(-222.0 - iy * 12.0)

    return [px, py]
#################################################################

#################################################################
def parseFileName(i):
    c1col = i.find('col_') + 4
    c2col = i.find('_row') 
    c1row = i.find('_row') + 4
    c2row = i.find('_X') 
    c1X = i.find('X_') + 2
    c2X = i.find('Y_')
    c1Y = c2X + 2
    c2Y = i.find('Z_')
    c1Z = c2Y + 2
    c2Z = i.find('RZ_')
    c1RZ = c2Z + 3
    c2RZ = i.find('J1_')
    c1J1 = c2RZ + 3
    c2J1 = i.find('J2_')
    c1J2 = c2J1 + 3
    c2J2 = i.find('J3_')
    c1J3 = c2J2 + 3
    c2J3 = i.find('J4_')
    c1J4 = c2J3 + 3
    c2J4 = i.find('.png')
    col = int(i[c1col:c2col])
    row = int(i[c1row:c2row])
    x = float(i[c1X:c2X])
    y = float(i[c1Y:c2Y])
    z = float(i[c1Z:c2Z])
    rz = float(i[c1RZ:c2RZ])
    j1 = float(i[c1J1:c2J1])
    j2 = float(i[c1J2:c2J2])
    j3 = float(i[c1J3:c2J3])
    j4 = float(i[c1J4:c2J4])

    return col, row, x, y, z, rz, j1, j2, j3, j4
#################################################################


#################################################################
def matchPoints(dirname):

    firstPointX = -132.0 + 22 * 12.0
    firstPointY = -222.0 - 29 * 12.0
    pointsFinal = []
    px = []
    py = []
    for i in os.listdir(dirname):
        if 'J1' not in i:
            continue
        col, row, x_, y_, z_, rz_, j1_, j2_, j3_, j4_ = parseFileName(i)
        xnom = firstPointX - col * 12.0
        ynom = firstPointY + row * 12.0
        px.append(xnom)
        py.append(ynom)
        a = [xnom, ynom, x_, y_, z_, rz_, j1_, j2_, j3_, j4_, dirname + '/' + i]
        pointsFinal.append(a)
    return [px, py], pointsFinal
#################################################################


#################################################################
def extractPoints(points):

    x = []
    y = []
    for p in points:
        x.append(p[2])
        y.append(p[3])
    return [x, y]
#################################################################


#################################################################
if __name__=='__main__':

    nominalPoints = getAllNominalPoints()

    #This directory must exist to store the fits
    fitOutput = 'fits'

    #listDir contains the name of the directory for a give set of pictures
    #and the threshold to be applied in the pattern reconition
    listDir = []
    listDir.append(['./newCalibrations/calibrationDataPoints3', 30])
    listDir.append(['./newCalibrations/Final_Calibration3', 100])
   
    #Some plotting to check consistency
    partialNominalPoints = []
    points = []
    for i in listDir:
        pnom, ppoints = matchPoints(i[0])
        partialNominalPoints.append(pnom)
        points.append(ppoints)

    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    ax.plot(nominalPoints[0], nominalPoints[1], '*b')
    for i in partialNominalPoints:
        ax.plot(i[0], i[1], '*m')

    meas = []
    for i in points:
        pmeas = extractPoints(i)
        meas.append(pmeas)
        ax.plot(pmeas[0], pmeas[1], 'om')
    
    plt.savefig('plot.png')

    finalList = []
    for pset in points:
        for i in pset:
            name = i[10]
            p = ProcessCalibrationPoint.ProcessCalibrationPoint(name, 'fitOutput')
            x, y, r, valid = p.fit(100)
            vector = [x, y, r]
            a = i
            a.extend(vector)
            if valid:
                finalList.append(a)
    
 
    with open('results.pickle', 'wb') as fp:
        pickle.dump(finalList, fp)


        



