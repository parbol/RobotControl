from optparse import OptionParser
from matplotlib.image import imread

from CameraClient.RobotCamera import RobotCamera
from RobotBrain.RobotController import RobotController


def Calibration():

    return True    

def Assembly():

    return True


if __name__ == "__main__":
    
    parser = OptionParser(usage="%prog --help")
    parser.add_option("-i", "--ip",              dest="ip",              type='string',  default='172.16.110.151', help="IP of the server.")
    parser.add_option("-p", "--port",            dest="port",            type=int,       default=1999,             help="Port of the server.")
    parser.add_option("-d", "--device",          dest="device",          type='string',  default='/dev/ttss0',     help="Device name")
    parser.add_option("-b", "--bauds",           dest="bauds",           type=int,       default=9600,             help="Bauds")
    (options, args) = parser.parse_args()

    #Initialize Camera
    robotCamera = RobotCamera(options.ip, options.port, 'picture.png')
    
    #Initialize Robot
    robotcontroller = RobotController(options.device, options.bauds)

    
    #########################################################################
    #En este punto ya podemos tomar fotos y también podemos mover el robot ##
    #########################################################################

    #Necesitamos 2 workflows
    #1.- Calibración -> Método Calibration()
    # Function -> x, y, z = robotCamera.GiveMeCalibrationPoint(x, y, z) 
    #2.- Ensamblaje


