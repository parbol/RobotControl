from optparse import OptionParser
from matplotlib.image import imread
import matplotlib.pyplot as plt
from CameraClient.RobotCamera import RobotCamera
from RobotBrain.RobotController import RobotController
from ExperimentalSetup.Camera import Camera
from ExperimentalSetup.Robot import Robot
from ExperimentalSetup.Table import Table
from ExperimentalSetup.CalibrationHandler import CalibrationHandler

import numpy as np

# Units
mm = 1

# Constants
# TODO - Check this value and units
Z_MOVE = 182 * mm  


if __name__ == "__main__":
    
    parser = OptionParser(usage="%prog --help")
    parser.add_option("-i", "--ip",              dest="ip",              type='string',  default='192.168.0.189', help="IP of the server.")
    parser.add_option("-p", "--port",            dest="port",            type=int,       default=8080,             help="Port of the server.")
    parser.add_option("-d", "--device",          dest="device",          type='string',  default='/dev/ttyUSB0',     help="Device name")
    parser.add_option("-b", "--bauds",           dest="bauds",           type=int,       default=115200,             help="Bauds")
    (options, args) = parser.parse_args()

    ################Initilize 3D setup model
    # The table
    table = Table(0.01, 0.0)
    # The physical camera
    caliHandler = CalibrationHandler()
    cali = caliHandler.getLastCalibration()

    # Generate the camera  
    camera = Camera(x = cali['cameraX'], y = cali['cameraY'],
                    z = cali['cameraZ'], psi = cali['cameraPsi'],
                    theta = cali['cameraTheta'], phi = cali['cameraPhi'],
                    cx = cali['c'], cy = cali['c'],
                    focaldistance = cali['focaldistance'],
                    focusdistance = cali['focusdistance'])

    # Generate the robot
    robot = Robot(cali['R1'], cali['R2'], cali['Z0'], table, camera)

    #Initialize Camera
    robotCamera = RobotCamera(options.ip, options.port, 'picture.png', robot3D)
    
    #Initialize Robot
    robotcontroller = RobotController(options.device, options.bauds, robotCamera, robot3D, True)
    # # HDI
    # z_pos  = np.linspace(128.3, 128.5, 10)
    # x_pos  = np.linspace(396.5, 398, 15)
    # y_pos  = np.linspace(-102.5, -100, 15)
    # print('*'*150)
    # print(x_pos, y_pos,z_pos)
    # for ix in x_pos:
    #     for iy in y_pos:
    #         for iz in z_pos:
    #             robotcontroller.goTo(ix, iy, iz, -72.226)
    #             pos = robotcontroller.getPositionXYZ()
    #             x = pos[0]
    #             y = pos[1]
    #             z = pos[2]
    #             robotcontroller.camera.changeFileName(f'PicturesHDI/picture_X{x}Y{y}Z{z}.png')
    #             robotcontroller.camera.takePic()
    # LGAD
    # z_pos  = np.linspace(127.2, 127.5, 10)
    # x_pos  = np.linspace(362.5, 364, 10)
    # y_pos  = np.linspace(-159.5, -158, 10)
    # print('*'*150)
    # print(x_pos, y_pos,z_pos)
    # for ix in x_pos:
    #     for iy in y_pos:
    #         for iz in z_pos:
    #             robotcontroller.goTo(ix, iy, iz, -72.226)
    #             pos = robotcontroller.getPositionXYZ()
    #             x = pos[0]
    #             y = pos[1]
    #             z = pos[2]
    #             robotcontroller.camera.changeFileName(f'PicturesLGAD/picture_X{x}Y{y}Z{z}.png')
    #             robotcontroller.camera.takePic()
    # ETROC
    z_pos  = np.linspace(127, 128.0, 1001)
    x_pos  = 377.0
    y_pos  = -161.5
    print('*'*150)
    print(x_pos, y_pos,z_pos)
    for iz in z_pos:
        robotcontroller.goTo(x_pos, y_pos, iz, -72.226)
        pos = robotcontroller.getPositionXYZ()
        x = pos[0]
        y = pos[1]
        z = pos[2]
        robotcontroller.camera.changeFileName(f'PicturesETROC-ZScan/picture_X{x:.4f}Y{y:.4f}Z{z:.4f}.png')
        robotcontroller.camera.takePic()
    robotcontroller.stop()

    #########################################################################
    #En este punto ya podemos tomar fotos y también podemos mover el robot ##
    #########################################################################

    #Necesitamos 2 workflows
    #1.- Calibración -> Método Calibration()
    # Function -> x, y, z = robotCamera.GiveMeCalibrationPoint(x, y, z) 
    #2.- Ensamblaje


