from optparse import OptionParser
from matplotlib.image import imread
import matplotlib.pyplot as plt
from CameraClient.RobotCamera import RobotCamera
from RobotBrain.RobotController import RobotController
from ExperimentalSetup.Camera import Camera
from ExperimentalSetup.Robot import Robot
from ExperimentalSetup.Table import Table

# Units
mm = 1

# Constants
# TODO - Check this value and units
Z_MOVE = 182 * mm  

def Calibration():
    # I need a list with the pin positions, in x,y,z or j1,j2,j3
    pin_positions = [(x1,y1,z1),]
    pin_center = []
    # Move the robot to initial position, at least correct z
    robot_position = robotcontroller.getPositionXYZ()
    robotcontroller.goTo(robot_position[0], robot_position[1], Z_MOVE, v)
    
    for (ix, iy, iz) in pin_positions:
        # Move to position in 2 steps, first fixed Z then go down. Take pic. Go up
        robot_position = robotcontroller.getPositionXYZ()
        robotcontroller.goTo(ix, iy, robot_position[2], v)
        robot_position = robotcontroller.getPositionXYZ()
        robotcontroller.goTo(robot_position[0], robot_position[1], iz, v)
        robot_position = robotcontroller.getPositionXYZ()

        # TODO Function to retrieve calibration
        x, y, z = RobotCamera.GiveMeCalibrationPoint(ix, iy, iz)
        pin_center.append((x, y, z))
        # Go up again
        robotcontroller.goTo(robot_position[0], robot_position[1], Z_MOVE, v)
        robot_position = robotcontroller.getPositionXYZ()
    return True

def Assembly():

    return True


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

    #Initialize Camera
    robotCamera = RobotCamera(options.ip, options.port, 'picture.png', robot3D)
    
    #Initialize Robot
    robotcontroller = RobotController(options.device, options.bauds, robotCamera, robot3D)

    robotcontroller.goTo(464.9, 0.0, 180.0, -72.234)

    
    #########################################################################
    #En este punto ya podemos tomar fotos y también podemos mover el robot ##
    #########################################################################

    #Necesitamos 2 workflows
    #1.- Calibración -> Método Calibration()
    # Function -> x, y, z = robotCamera.GiveMeCalibrationPoint(x, y, z) 
    #2.- Ensamblaje


