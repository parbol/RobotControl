from optparse import OptionParser
from matplotlib.image import imread
import matplotlib.pyplot as plt
from CameraClient.RobotCamera import RobotCamera
from RobotBrain.ETLController import ETLController
from ExperimentalSetup.Camera import Camera
from ExperimentalSetup.Robot import Robot
from ExperimentalSetup.Table import Table
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
    camera = Camera(x = 2.0, y = 0.0, z = -27.0, psi = 0.0, theta = 0.0, phi = 0.0, cx = 0.5, cy = 0.5, focaldistance = 10, sigmaCamera = 0.001)
    # The graphs
    fig = plt.figure(figsize = (16, 8), layout="constrained")
    gs0 = fig.add_gridspec(1, 2, width_ratios=[2, 1])
    ax1 = fig.add_subplot(gs0[0], projection = '3d')
    gs1 = gs0[1].subgridspec(2,1)
    ax2 = fig.add_subplot(gs1[0])
    ax3 = fig.add_subplot(gs1[1])
    ax1.xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax1.yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax1.zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax1.set_xlabel('x [cm]')
    ax1.set_ylabel('y [cm]')
    ax1.set_zlabel('z [cm]')
    ax2.set_xlabel('x [cm]')
    ax2.set_ylabel('y [cm]')
    ax3.set_xlabel('z [cm]')
    ax3.set_ylabel('y [cm]')
    ax1.axes.set_xlim3d(left=-70, right=70.0)
    ax1.axes.set_ylim3d(bottom=-70, top=70.0)
    ax2.axes.set_xlim((-40.0, 70.0))
    ax2.axes.set_ylim((-70.0, 40.0))
    ax3.axes.set_xlim((-1.0, 1.0))
    ax3.axes.set_ylim((-1.0, 1.0))
    # The 3D model of the robot
    robot3D = Robot(50.0, 30.0, 30.0, 40, table, camera, fig, ax1, ax2, ax3)

    # Initialize Camera
    # robotCamera = RobotCamera(options.ip, options.port, 'picture.png', robot3D)
    
    # Initialize Robot
    # etlcontroller = ETLController(options.device, options.bauds, robotCamera, robot3D, False)
    etlcontroller = ETLController(options.device, options.bauds, None, robot3D, False)
    
    # # Move to take some photos 
    # mark_pos = [x, y, z ,rz] # TODO
    # etlcontroller.safeMovement(mark_pos[0], mark_pos[1], mark_pos[2], mark_pos[3])
    # robotCamera.changeFileName(f"Pictures/picture.png")
    # robotCamera.takePic()
    
    # Pick picker tool
    etlcontroller.grabPickerTool()

    # Move 2 pieces one on top of the other
    sensor_pos = [-361.43, -421.93, 136, 107]
    finalsensor_pos = [286, -482, 150, 107] # Rotate piece 90deg to the left
    etlcontroller.grabAssemblyPart(sensor_pos[0], sensor_pos[1], sensor_pos[2], sensor_pos[3])
    etlcontroller.releaseAssemblyPart(finalsensor_pos[0], finalsensor_pos[1], finalsensor_pos[2], finalsensor_pos[3])
    # Next piece
    metal_pos = [-302.28, -191.23, 140, 107]
    finalmetal_pos = [286, -482, 150, 107] # Rotate piece 90deg to the left
    etlcontroller.grabAssemblyPart(metal_pos[0], metal_pos[1], metal_pos[2], metal_pos[3])
    etlcontroller.releaseAssemblyPart(finalmetal_pos[0], finalmetal_pos[1], finalmetal_pos[2], finalmetal_pos[3])

    # Release picker tool
    etlcontroller.releasePickerTool()
    
    etlcontroller.exit()

    #########################################################################
    #En este punto ya podemos tomar fotos y también podemos mover el robot ##
    #########################################################################

    #Necesitamos 2 workflows
    #1.- Calibración -> Método Calibration()
    # Function -> x, y, z = robotCamera.GiveMeCalibrationPoint(x, y, z) 
    #2.- Ensamblaje


