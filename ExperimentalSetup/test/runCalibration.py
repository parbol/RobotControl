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


if __name__ == "__main__":

    parser = OptionParser(usage="%prog --help")
    parser.add_option("-i", "--input",           dest="input",           type='string',  default='calibration.pkl',    help="Pickle file with calibration points.")
    (options, args) = parser.parse_args()

    with open (options.input, 'rb') as fp:
        itemlist = pickle.load(fp)


    caliHandler = CalibrationHandler()
    cali = caliHandler.getLastCalibration()
    #cali['cameraX'] = -1.100968
    #cali['cameraY'] = -95.196756
    #cali['cameraPsi'] = 3.1415
    cali['cameraX'] = -1.23001339
    cali['cameraY'] = -95.37271516
    cali['cameraPsi'] = 1.904899668752405

    endog, exdog = prepareInput(itemlist, cali['focusdistance'])
   
    #Table
    table = Table(0.01, 0.0)

    

    #mode 1 is for debugging a single point
    #mode 2 is for the actual likelihood
    #mode 3 is for debugging the angle
    #mode 4 is for debugging the full table
    
    mode = 4
    
    
    ##################################Debug 1#################################
    ppoint = 0
    
    if mode == 1:
    
        # Generate the camera  
        camera = Camera(x = cali['cameraX'], y = cali['cameraY'],
                        z = cali['cameraZ'], psi = cali['cameraPsi'],
                        theta = cali['cameraTheta'], phi = cali['cameraPhi'],
                        cx = cali['c'], cy = cali['c'],
                        focaldistance = cali['focaldistance'],
                        focusdistance = cali['focusdistance'])

        # Generate the robot
        robot = Robot(cali['R1'], cali['R2'], cali['Z0'], table, camera)
    
    
        #Position of the robot
        robotPosition = np.asarray([np.pi / 180.0 * exdog[ppoint][0], np.pi / 180.0 * exdog[ppoint][1], exdog[ppoint][2], np.pi / 180.0 * (exdog[ppoint][3])])
        #robotPosition = np.asarray([0.0, 0.0, exdog[0][2], 90 * np.pi/180.0])
        robot.JMoveRobotTo(robotPosition)
    
        print('Posicion del robot:', robot.position)
        print('Posicion del robot ux:', robot.ux)
        print('Posicion del robot uy:', robot.uy)
        print('Posicion del robot uz:', robot.uz)

        print('Posicion del robot J:', robot.J1, robot.J2, robot.J3, robot.J4)
        print('Posicion de la cámara:', robot.camera.r)
        print('Posicion camara eje X:', robot.camera.ux) 
        print('Posicion camara eje Y:', robot.camera.uy) 
        print('Posicion camara eje Z:', robot.camera.uz) 
        print('Posición nominal del punto:', endog[ppoint])

            
        #Nominal position of the point in global coordinates
        nominalPosition = endog[ppoint]
        #Nominal position of the point in the camera projection
        xn, yn = robot.point3DToCameraProjection(nominalPosition)
        newPosition = robot.cameraProjectionToPoint3D(np.asarray([xn,yn]))
        print('Nominal position:', nominalPosition)        
        print('Recovered position:', newPosition)
        rn = np.asarray([xn, yn])
        #Measurement in the camera system 
        rm = np.asarray([exdog[ppoint][4], exdog[ppoint][5]])
        print('camera:', camera.r)
        print('camera ux:', camera.ux)
        print('camera uy:', camera.uy)
        print('camera uz:', camera.uz)

        print('xn:', xn, 'yn:', yn)
        print('xm:', rm[0], 'ym:', rm[1])


    if mode == 2:
        
        # Generate the camera  
        camera = Camera(x = cali['cameraX'], y = cali['cameraY'],
                        z = cali['cameraZ'], psi = cali['cameraPsi'],
                        theta = cali['cameraTheta'], phi = cali['cameraPhi'],
                        cx = cali['c'], cy = cali['c'],
                        focaldistance = cali['focaldistance'],
                        focusdistance = cali['focusdistance'])

        # Generate the robot
        robot = Robot(cali['R1'], cali['R2'], cali['Z0'], table, camera)
        
        #Likelihood
        lhood = CameraLikelihood(endog, exdog, robot)
        res = lhood.fit()
        chi2 = lhood.check()
        print("Parameters:", res.params)
        print("Standard errors:", res.bse)
        print("Initial chi2:", lhood.chi2k[0], "Final chi2", chi2)
        print('Mean distance:', np.sqrt(chi2/len(exdog)), 'mm')
        print('C', robot.camera.cx)
        #caliHandler.writeNewCalibration(R1 = cali['R1'], R2 = cali['R2'],
        #                                Z0 = cali['Z0'], focaldistance = cali['focaldistance'],
        #                                focusdistance = cali['focusdistance'], cameraTheta = cali['cameraTheta'],
        #                                cameraPhi = cali['cameraPhi'], c = cali['c'],
        #                                cameraX = res.params[0],
        #                                cameraY = res.params[1],
        #                                cameraZ = cali['cameraZ']
        #                                cameraPsi = res.params[2])

    
    if mode == 3:
        
        for i in range(1):    
            
            chi2 = 0.0
            angle = 2.0*np.pi/50.0 * i
            angle = cali['cameraPsi']
            print('angle:', angle*180.0/np.pi)
            # Generate the camera  
            camera = Camera(x = cali['cameraX'], y = cali['cameraY'],
                            z = cali['cameraZ'], psi = angle,
                            theta = cali['cameraTheta'], phi = cali['cameraPhi'],
                            cx = cali['c'], cy = cali['c'],
                            focaldistance = cali['focaldistance'],
                            focusdistance = cali['focusdistance'])

            # Generate the robot
            robot = Robot(cali['R1'], cali['R2'], cali['Z0'], table, camera)
        
            #Position of the robot
            robotPosition = np.asarray([np.pi / 180.0 * exdog[ppoint][0], np.pi / 180.0 * exdog[ppoint][1], exdog[ppoint][2], np.pi / 180.0 * (exdog[ppoint][3])])
            #robotPosition = np.asarray([0.0, 0.0, exdog[0][2], 90 * np.pi/180.0])
            robot.JMoveRobotTo(robotPosition)
    
            #print('Posicion del robot:', robot.position)
            #print('Posicion del robot ux:', robot.ux)
            #print('Posicion del robot uy:', robot.uy)
            #print('Posicion del robot uz:', robot.uz)

            #print('Posicion del robot J:', robot.J1, robot.J2, robot.J3, robot.J4)
            #print('Posicion de la cámara:', robot.camera.r)
            #print('Posicion camara eje X:', robot.camera.ux) 
            #print('Posicion camara eje Y:', robot.camera.uy) 
            #print('Posicion camara eje Z:', robot.camera.uz) 
            #print('Posición nominal del punto:', endog[ppoint])

            nominalPosition1 = np.copy(endog[ppoint])
            nominalPosition2 = np.copy(endog[ppoint])
            nominalPosition2[1] = nominalPosition2[1] - 0.1
            nominalPosition3 = np.copy(endog[ppoint])
            nominalPosition3[1] = nominalPosition3[1] - 0.2
            nominalPosition4 = np.copy(endog[ppoint])
            nominalPosition4[1] = nominalPosition4[1] - 0.3
            nominalPosition5 = np.copy(endog[ppoint])
            nominalPosition5[1] = nominalPosition5[1] - 0.3
            nominalPosition5[0] = nominalPosition5[0] - 0.1
            nominalPosition6 = np.copy(endog[ppoint])
            nominalPosition6[1] = nominalPosition6[1] - 0.2
            nominalPosition6[0] = nominalPosition6[0] - 0.1
            xt = np.asarray([nominalPosition1[0], nominalPosition2[0], nominalPosition3[0], nominalPosition4[0], nominalPosition5[0], nominalPosition6[0]])
            yt = np.asarray([nominalPosition1[1], nominalPosition2[1], nominalPosition3[1], nominalPosition4[1], nominalPosition5[1], nominalPosition6[1]])
            fig, ax = plt.subplots()
            ax.plot(xt, yt)
            ax.set_xlim(-133.0, -131.0)
            ax.set_ylim(-295.0, -293.0)
            plt.savefig('plot2.png')
            #Nominal position of the point in global coordinates
            #Nominal position of the point in the camera projection
            xn1, yn1 = robot.point3DToCameraProjection(nominalPosition1)
            xn2, yn2 = robot.point3DToCameraProjection(nominalPosition2)
            xn3, yn3 = robot.point3DToCameraProjection(nominalPosition3)
            xn4, yn4 = robot.point3DToCameraProjection(nominalPosition4)
            xn5, yn5 = robot.point3DToCameraProjection(nominalPosition5)
            xn6, yn6 = robot.point3DToCameraProjection(nominalPosition6)
            x = np.asarray([xn1, xn2, xn3, xn4, xn5, xn6])
            y = -np.asarray([yn1, yn2, yn3, yn4, yn5, yn6])
            fig, ax = plt.subplots()
            #ax.set_aspect('equal', adjustable='box')
            ax.plot(x, y)
            ax.set_xlim(0, 2064)
            ax.set_ylim(-1544, 0)
            plt.savefig('plot.png')
            #Measurement in the camera system 
            rm = np.asarray([exdog[ppoint][4], exdog[ppoint][5]])
            #print('camera:', camera.r)
            #print('camera ux:', camera.ux)
            #print('camera uy:', camera.uy)
            #print('camera uz:', camera.uz)
            time.sleep(1)



    if mode == 4:

        for i in range(50):    
            
            chi2 = 0.0
            angle = 2.0*np.pi/50.0 * i
            camera = Camera(x = cali['cameraX'], y = cali['cameraY'],
                            z = cali['cameraZ'], psi = angle,
                            theta = cali['cameraTheta'], phi = cali['cameraPhi'],
                            cx = cali['c'], cy = cali['c'],
                            focaldistance = cali['focaldistance'],
                            focusdistance = cali['focusdistance'])

            # Generate the robot
            robot = Robot(cali['R1'], cali['R2'], cali['Z0'], table, camera)

            #Position of the robot
            xm = []
            ym = []
            xn = []
            yn = []
            for ppoint, ex in enumerate(exdog):
        
                robotPosition = np.asarray([np.pi / 180.0 * exdog[ppoint][0], np.pi / 180.0 * exdog[ppoint][1], exdog[ppoint][2], np.pi / 180.0 * (exdog[ppoint][3])])
                #robotPosition = np.asarray([0.0, 0.0, exdog[0][2], 90 * np.pi/180.0])
                robot.JMoveRobotTo(robotPosition)
    
                
                pm = np.asarray([exdog[ppoint][4], exdog[ppoint][5]])
                rm = robot.cameraProjectionToPoint3D(pm)

                xn.append(endog[ppoint][0])
                yn.append(endog[ppoint][1])
                xm.append(rm[0])
                ym.append(rm[1])
                
                xn_ = endog[ppoint][0]
                yn_ = endog[ppoint][1]
                xm_ = rm[0]
                ym_ = rm[1]
                chi2 = chi2 + (xn_-xm_)**2 + (yn_-ym_)**2
            
            print('Angle', angle*180/np.pi, 'chi2:', np.sqrt(chi2/len(endog)))

            fig, ax = plt.subplots()
            ax.plot(xm, ym, 'g.', )
            ax.plot(xn, yn, 'r.')
            ax.set_xlim(-110, -75)
            ax.set_ylim(-355, -320)
            plt.savefig('plot.png')
            time.sleep(1)            
       


