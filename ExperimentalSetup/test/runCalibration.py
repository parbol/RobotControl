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

    endog = []
    exdog = []
    for i in data:
        #The nominal position in global coordinates. The z is taken from the measurement itself.
        #vector a contains the nominal position of the points [xn, yn, zn]
        a = [i[0], i[1], i[4] + focusdistance]
        endog.append(a)
        #vector b contains b = [j1, j2, j3, j4, xm, ym, rm] where xm, ym and rm are the measurements x, y and radius
        b = [i[6], i[7], i[8], i[9], i[11], i[12], i[13]]
        exdog.append(b)

    return endog, exdog


if __name__ == "__main__":

    parser = OptionParser(usage="%prog --help")
    parser.add_option("-i", "--input",           dest="input",           type='string',  default='calibration.pkl',    help="Pickle file with calibration points.")
    (options, args) = parser.parse_args()

    with open (options.input, 'rb') as fp:
        itemlist = pickle.load(fp)

    #Get calibrations
    caliHandler = CalibrationHandler('calibrations.txt')
    cali = caliHandler.getLastCalibration()
    
   
    #Table
    table = Table(0.01, 0.0)

    # Generate the camera  
    camera = Camera(x = cali['cameraX'], y = cali['cameraY'],
                    z = cali['cameraZ'], psi = cali['cameraPsi'],
                    theta = cali['cameraTheta'], phi = cali['cameraPhi'],
                    cx = cali['c'], cy = cali['c'],
                    focaldistance = cali['focaldistance'],
                    focusdistance = cali['focusdistance'])

    #Likelihood
    lhood = CameraLikelihood(endog, exdog, robot)
    res = lhood.fit()
    chi2 = lhood.check()
    
    #Arrangement to estimate the angle
    x = res.params[2]
    y = res.params[3]
    ex = res.bse[2]
    ey = res.bse[3]
    psi = np.atan2(x, y)
    errorPsi = 1.0/(y**2+x**2) * np.sqrt((y*ex)**2 + (x*ey)**2)
 
    print('-------------------------------Final results----------------------------')
    print('Parameters:')
    print(f'cameraX: {res.params[0]} +/- {res.bse[0]}')
    print(f'cameraY: {res.params[1]} +/- {res.bse[1]}')
    print(f'cameraPsi: {psi} +/- {errorPsi}')
    print(f'C: {res.params[4]} +/- {res.bse[4]}')
    print(f'Phi0_robot: {res.params[5]} +/- {res.bse[5]}')
    print('Chi2 info:')
    print("Initial chi2:", lhood.chi2k[0], "Final chi2", chi2)
    print('Mean distance:', np.sqrt(chi2/len(exdog)), 'mm')
    
    caliHandler.writeNewCalibration(R1 = cali['R1'], R2 = cali['R2'],
                                    Z0 = cali['Z0'], focaldistance = cali['focaldistance'],
                                    focusdistance = cali['focusdistance'], cameraTheta = cali['cameraTheta'],
                                    cameraPhi = cali['cameraPhi'], c = res.params[4],
                                    cameraX = res.params[0],
                                    cameraY = res.params[1],
                                    cameraZ = cali['cameraZ'],
                                    cameraPsi = psi)

   
