from optparse import OptionParser
from matplotlib.image import imread
import matplotlib.pyplot as plt
from CameraClient.RobotCamera import RobotCamera
from RobotBrain.ETLController import ETLController
from ExperimentalSetup.Camera import Camera
from ExperimentalSetup.Robot import Robot
from ExperimentalSetup.Table import Table
import numpy as np

if __name__ == "__main__":
    
    parser = OptionParser(usage="%prog --help")
    parser.add_option("-i", "--ip", dest="ip", type="string", default="192.168.0.189", help="IP of the camera server.")
    parser.add_option("-p", "--port", dest="port", type=int, default=8080, help="Port of the camera server.")
    parser.add_option("-d", "--device", dest="device", type="string", default="/dev/ttyUSB0", help="Robot device name.")
    parser.add_option("-b", "--bauds", dest="bauds", type=int, default=115200, help="Robot bauds.")
    (options, args) = parser.parse_args()

    ################Initilize 3D setup model
    # The table
    table = Table(0.01, 0.0)
    # The physical camera
    camera = Camera(x = 2.0, y = 0.0, z = -27.0, psi = 0.0, theta = 0.0, phi = 0.0, cx = 0.5, cy = 0.5, focaldistance = 10, focusdistance = 0.001)
    # The 3D model of the robot
    robot3D = Robot(50.0, 30.0, 40, table, camera)

    # init_hole_pos = [176.73, -468.21, 180, 28.06]
    # step_x = 1.2
    # step_y = 1.2
    # Initialize Camera
    robotCamera = RobotCamera(options.ip, options.port, 'picture.png', robot3D)
    
    # Initialize Robot
    etlcontroller = ETLController(options.device, options.bauds, robotCamera, robot3D, False)
    # etlcontroller.camera.set_exposure(0.00025)
    
    # TODO - Define glue plate points position
    init_positions = [# [176.73, -485.67, 180, 28.08], # Old position not working now
                     #  [175.80, -485.67, 180, 28.08],
                     #  [222.79, -540.64, 180, 72.53],
                     # [130.61, -473.97, 180, 00.02],
                      [63.45, -502.00, 180, -44.50],
                      [35.21, -563.20, 180, -85.42],
                      # [43.37, -609.62, 180, -113.62]
                      ]

    n_holes_x = 10
    n_holes_y = 3
    step_x = 12
    step_y = 12
     
    for i, init_pos in enumerate(init_positions):
        print(i, init_pos)
        if i == -1:
            init_x = 9
        else:
            init_x = 0
        position_xyzrz = etlcontroller.getPositionXYZ()
        etlcontroller.safeMovement(position_xyzrz[0], position_xyzrz[1], init_pos[2], init_pos[3])
        for ix in range(init_x, n_holes_x):
            if i == -1 and ix == 9:
                init_y = 1
            else:
                init_y = 0

            for iy in range(init_y, n_holes_y):
                print(f"Col {ix}, Row {iy}")
                x_hole = init_pos[0] - ix*step_x
                y_hole = init_pos[1] + iy*step_y

                etlcontroller.safeMovement(x_hole, y_hole, init_pos[2], None)
                summary, focus_z, fraction = etlcontroller.fullAutoFocus(127, is_double=True)   
                etlcontroller.changeZ(focus_z)
                # Take pic
                position_xyzrz = etlcontroller.getPositionXYZ()
                position_j1j2j3j4 = etlcontroller.getPositionJ1J2J3_deg()
                x, y, z, rz = position_xyzrz
                j1, j2, j3, j4 = position_j1j2j3j4
                etlcontroller.camera.changeFileName(f"GluePlate/Final_Calibration2/picture_col_{ix}_row{iy}_X_{x:.3f}Y_{y:.3f}Z_{z:.3f}RZ_{rz:.3f}J1_{j1:.3f}J2_{j2:.3f}J3_{j3:.3f}J4_{j4:.3f}.png")
                etlcontroller.camera.takePic()
    
    # # Photo on the ruller
    # ruller_pos = [-21.91, -437.75, 180, 0.02]
    # etlcontroller.safeMovement(ruller_pos[0], ruller_pos[1], ruller_pos[2], ruller_pos[3])
    # summary, focus_z, fraction = etlcontroller.fullAutoFocus(129, is_double=True)   
    # etlcontroller.changeZ(focus_z)
    # # Take pic
    # etlcontroller.camera.changeFileName(f"RullerPic/picture_002_rz0.02.png")
    # etlcontroller.camera.takePic()

    etlcontroller.exit()
