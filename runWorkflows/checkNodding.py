from optparse import OptionParser
from matplotlib.image import imread
import matplotlib.pyplot as plt
from CameraClient.RobotCamera import RobotCamera
from RobotBrain.ETLController import ETLController
from ExperimentalSetup.Camera import Camera
from ExperimentalSetup.Robot import Robot
from ExperimentalSetup.Table import Table
import numpy as np
import sys
from datetime import datetime

if __name__ == "__main__":
    
    parser = OptionParser(usage="%prog --help")
    parser.add_option("-i", "--ip", dest="ip", type="string", default="192.168.0.189", help="IP of the camera server.")
    parser.add_option("-p", "--port", dest="port", type=int, default=8080, help="Port of the camera server.")
    parser.add_option("-d", "--device", dest="device", type="string", default="/dev/ttyUSB0", help="Robot device name.")
    parser.add_option("-b", "--bauds", dest="bauds", type=int, default=115200, help="Robot bauds.")
    parser.add_option("-n", "--npic",           dest="npic",           type=int,       default=50,             help="N pictures")
    parser.add_option("-t", "--deadtime",           dest="dadetime",           type=bool,       default=False,             help="Use dead time")

    (options, args) = parser.parse_args()

    ################Initilize 3D setup model
    # The table
    table = Table(0.01, 0.0)
    # The physical camera
    camera = Camera(x = 2.0, y = 0.0, z = -27.0, psi = 0.0, theta = 0.0, phi = 0.0, cx = 0.5, cy = 0.5, focaldistance = 10, focusdistance = 0.001)
    # The 3D model of the robot
    robot3D = Robot(50.0, 30.0, 40, table, camera)

    # Initialize Camera
    robotCamera = RobotCamera(options.ip, options.port, 'picture.png', robot3D)
    
    # Initialize Robot
    etlcontroller = ETLController(options.device, options.bauds, robotCamera, robot3D, False)
    etlcontroller.camera.set_exposure(0.025)
    
    if options.deadtime:
        dead_time = list(range(0, options.npic*5, 5))
    else:
        dead_time = [0]*options.npic
    for i_dead_time in dead_time:
        # Generate date
        now = datetime.now()
        date_str = f"{now.year}-{now.month}-{now.day}-{now.hour}-{now.minute}"
        
        # Corner 0,0
        pic_position = [177, -485.67, 180, 28.08]
        etlcontroller.safeMovement(pic_position[0], pic_position[1], pic_position[2], pic_position[3])
        summary, focus_z, fraction = etlcontroller.fullAutoFocus(127, is_double=True)   
        etlcontroller.changeZ(focus_z)
        if options.deadtime:
            etlcontroller.waitTime(i_dead_time)
        # Take pic
        position_xyzrz = etlcontroller.getPositionXYZ()
        position_j1j2j3j4 = etlcontroller.getPositionJ1J2J3_deg()
        x, y, z, rz = position_xyzrz
        j1, j2, j3, j4 = position_j1j2j3j4
        etlcontroller.camera.changeFileName(f"RepeatibilityTest/{date_str}_X_{x:.3f}Y_{y:.3f}Z_{z:.3f}RZ_{rz:.3f}J1_{j1:.3f}J2_{j2:.3f}J3_{j3:.3f}J4_{j4:.3f}.png")
        etlcontroller.camera.takePic()

    etlcontroller.exit()
