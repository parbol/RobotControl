from optparse import OptionParser
from matplotlib.image import imread
import matplotlib.pyplot as plt
from CameraClient.RobotCamera import RobotCamera
from RobotBrain.RobotController import RobotController
from ExperimentalSetup.Camera import Camera
from ExperimentalSetup.Robot import Robot


# Units
mm = 1

# Constants
# TODO - Check this value and units
Z_MOVE = 182 * mm  


if __name__ == "__main__":
    
    parser = OptionParser(usage="%prog --help")
    parser.add_option("-i", "--ip",              dest="ip",              type='string',  default='192.168.0.189',    help="IP of the server.")
    parser.add_option("-p", "--port",            dest="port",            type=int,       default=8080,               help="Port of the server.")
    parser.add_option("-d", "--device",          dest="device",          type='string',  default='/dev/ttyUSB0',     help="Device name")
    parser.add_option("-b", "--bauds",           dest="bauds",           type=int,       default=115200,             help="Bauds")
    (options, args) = parser.parse_args()

    ################Initilize 3D setup model
    #Initialize Camera
    robotCamera = RobotCamera(options.ip, options.port, 'picture.png', robot3D)
    
    #Initialize Robot
    robotcontroller = RobotController(options.device, options.bauds, robotCamera, robot3D)

    
