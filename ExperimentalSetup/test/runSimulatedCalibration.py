import math
import numpy as np
import matplotlib.pyplot as plt
import sys
from optparse import OptionParser
from ExperimentalSetup.Table import Table
from ExperimentalSetup.Camera import Camera
from ExperimentalSetup.Robot import Robot
from ExperimentalSetup.Likelihood import CameraLikelihood
from ExperimentalSetup.CalibrationHandler import CalibrationHandler
import pickle
import time



def prepareInput(data, focusdistance):

    # This distance is the distance from the objective to the hole in Z. Probably should be revised.
    endog = []
    exdog = []
    for i in data:
        #The nominal position in global coordinates. The z is taken from the measurement itself.
        #[xn, yn, x, y, z, jz, j1, j2, j3, j4, name, xm, ym, rm]
        a = [i[0], i[1], i[4] + focusdistance]
        endog.append(a)
        #b = [i[6], i[7], i[8], i[9], i[11], i[12]]
        b = [i[6], i[7], i[8], i[9], i[11], i[12]]
        exdog.append(b)

    return endog, exdog



def getMeasurements(N, sigmax, sigmay, robot, p):

    valid, J1, J2, Z = robot.fromCartesianToInner(p)
    if not valid:
        return []
    centerJ = [J1, J2, Z-36.0, 0.0]
    robot.JMoveRobotTo(centerJ)
    measurements = []
    for i in range(N):
        Jz = i * 2.0 * np.pi / N
        newPointJ = np.copy(centerJ)
        newPointJ[3] = Jz
        robot.JMoveRobotTo(newPointJ)
      
        cameraPos = np.copy(robot.camera.r)
        phiCamera = np.atan2(robot.camera.r0[1], robot.camera.r0[0])
        #deltaX = np.random.uniform(-1.4, 1.4)
        #deltaY = np.random.uniform(-1.4, 1.4)
        #cameraPos[0] = cameraPos[0] + deltaX
        #cameraPos[1] = cameraPos[1] + deltaY
        valid, J1, J2, Z = robot.fromCartesianToInner(cameraPos)
        newCenterJ = [J1, J2, Z, np.pi]
        robot.JMoveRobotTo(newCenterJ)
        
        xn, yn = robot.point3DToCameraProjection(p)
        measurements.append([newCenterJ[0].item()*180.0/np.pi, newCenterJ[1].item()*180.0/np.pi, newCenterJ[2].item(), newCenterJ[3]*180.0/np.pi, xn.item(), yn.item()])

    return measurements

    




if __name__ == "__main__":

    parser = OptionParser(usage="%prog --help")
    parser.add_option("-i", "--input",           dest="input",           type='string',  default='calibration.pkl',    help="Pickle file with calibration points.")
    (options, args) = parser.parse_args()

    with open (options.input, 'rb') as fp:
        itemlist = pickle.load(fp)


    endog, exdog = prepareInput(itemlist, 36.0)
  
    nominalPositions = []
    for p in endog:
        p2 = p.copy()
        p2[1] = -p2[1]
        nominalPositions.append(p)
        #nominalPositions.append(p2)

    
    camera = Camera(x = 1.0, y = 12.0,
                    z = 0.0, psi = np.pi/4,
                    theta = 0.0, phi = 0.0,   
                    cx = -256.0, cy = -256.0,
                    focaldistance = 200.0,
                    focusdistance = 36.0)

    # Generate the robot
    robot = Robot(380.0, 240.0, 360, None, camera)
    
    endog2 = []
    exdog2 = []
    for p in nominalPositions:

        measurements = getMeasurements(1, 1.0, 1.0, robot, np.asarray(p)) 
        exdog2.extend(measurements)
        for j in range(len(measurements)):
            endog2.extend([p])
        
    print(endog2)
    # Generate the camera  
    camera2 = Camera(x = 0.0, y = 0.0,
                    z = 0.0, psi = 0.0,
                    theta = 0.0, phi = 0.0,
                    cx = -256.0, cy = -256.0,
                    focaldistance = 200.0,
                    focusdistance = 36.0)

    # Generate the robot
    robot2 = Robot(380.0, 240.0, 360.0, None, camera2)
        
    #Likelihood
    lhood = CameraLikelihood(endog2, exdog2, robot2)
    res = lhood.fit()
    chi2 = lhood.check()
    print("Parameters:", res.params)
    print("Standard errors:", res.bse)
    print("Initial chi2:", lhood.chi2k[0], "Final chi2", chi2)
    print('Mean distance:', np.sqrt(chi2/len(exdog)), 'mm')
      