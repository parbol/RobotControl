import ImageAnalysis.ProcessCalibrationPoint as ProcessCalibrationPoint
import os
import pickle

#################################################################
def produceCalibrationPoints():

    firstPointX = -132.0
    firstPointY = -222.0

    #This has to be adjusted by hand
    offsetCameraX = 20 
    offsetCameraY = 20

    stepx = 12
    stepy = 12

    nX = 22
    nY = 30

    startY = 6
    startX = 0
    points = [] 
    for ix in range(startX, startX+10):
        for iy in range(startY, startY+10):
            points.append([firstPointX + stepx*ix, firstPointY - stepy *iy])
    
    return points
#################################################################


#################################################################
def parseFileName(i):

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
    x = float(i[c1X:c2X])
    y = float(i[c1Y:c2Y])
    z = float(i[c1Z:c2Z])
    rz = float(i[c1RZ:c2RZ])
    j1 = float(i[c1J1:c2J1])
    j2 = float(i[c1J2:c2J2])
    j3 = float(i[c1J3:c2J3])
    j4 = float(i[c1J4:c2J4])

    return x, y, z, rz, j1, j2, j3, j4
#################################################################


#################################################################
def matchPoints(dirname, nominalPoints):
    
    x = []
    y = []
    z = []
    rz = []
    j1 = [] 
    j2 = []
    j3 = []
    j4 = []
    name = []
    xset = set()
    yset = set()
    for i in os.listdir(dirname):
        if 'J1' not in i:
            continue
        x_, y_, z_, rz_, j1_, j2_, j3_, j4_ = parseFileName(i)
        xset.add(x_)
        yset.add(y_)
        x.append(x_)
        y.append(y_)
        z.append(z_)
        rz.append(rz_)
        j1.append(j1_)
        j2.append(j2_)
        j3.append(j3_)
        j4.append(j4_)
        name.append(dirname + '/' + i)

    pointsMeasured = [[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0] for i in range(len(xset)*len(yset))]
    for ix, xval in enumerate(sorted(xset)):
        for iy, yval in enumerate(sorted(yset, reverse=True)):
            for k, xxval in enumerate(x):
                if x[k] == xval and y[k] == yval:
                    pointsMeasured[ix * len(yset) + iy] = [x[k], y[k], z[k], rz[k], j1[k], j2[k], j3[k], j4[k], name[k]]

    pointsFinal = []
    for i, c in enumerate(pointsMeasured):
        a = nominalPoints[i]
        a.extend(pointsMeasured[i])
        pointsFinal.append(a)

    return pointsFinal
#################################################################


#################################################################
if __name__=='__main__':

    nominalPoints = produceCalibrationPoints()
    points = matchPoints('./calibrationDataPoints', nominalPoints)
    finalList = []
    for i in points:
        name = i[10]
        p = ProcessCalibrationPoint.ProcessCalibrationPoint(name, 'fits')
        x, y, r, valid = p.fit()
        vector = [x, y, r]
        a = i
        a.extend(vector)
        finalList.append(a)

    with open('results.txt', 'wb') as fp:
        pickle.dump(finalList, fp)


        



