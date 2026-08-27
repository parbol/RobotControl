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

    # Initialize Camera
    robotCamera = RobotCamera(options.ip, options.port, 'picture.png', robot3D)
    
    # Initialize Robot
    etlcontroller = ETLController(options.device, options.bauds, robotCamera, robot3D, False)
    etlcontroller.camera.set_exposure(0.025)
    
    # TODO - Define glue plate points position
    # Corner 0,0
    init_positions = [# [176.73, -485.67, 180, 28.08], # Old position not working now
                     [177, -485.67, 180, 28.08],
                     # # [222.79, -541, 180, 72.53], Changed on 6th august, i dont know why 
                     # [223.29, -543.5, 180, 72.53],
                     # [130.61, -473.97, 180, 00.02],
                     # [63.45, -502.00, 180, -44.50],
                     # [35.21, -563.20, 180, -85.42],
                     #  # [43.37, -609.62, 180, -113.62] # Not use cabling under the arm
                      ]
    final_positions = [
                     [-85.87, -221.83, 180, 28.08],
                     [-40.37, -278.97, 180, 72.53],
                     [-130.46, -209.66, 180, 00.02],
                     # TODO - Be aware of cable collisions while rotating
                     #[63.45, -502.00, 180, -44.50],
                     #[35.21, -563.20, 180, -85.42],
                      # [43.37, -609.62, 180, -113.62] # Not use cabling under the arm
                      ]

    max_holes_x = 23
    # max_holes_y = 30 # Only 24 accesible without collision
    max_holes_y = 23
    n_holes_x = 23
    n_holes_y = 23
    
    for iteration in range(5):

        for i in range(min(len(init_positions),len(final_positions))):
            print(i, init_positions[i], final_positions[i])
            init_pos = init_positions[i]
            final_pos = final_positions[i]
            
            x_positions = np.linspace(init_pos[0], final_pos[0], max_holes_x)
            y_positions = np.linspace(init_pos[1], final_pos[1], max_holes_y)

            if i == 1:
                init_x = 1
            else:
                # init_x = max_holes_x - 1
                init_x = 0

            # x_hole_indices = np.arange(init_x, max_holes_x-n_holes_x, -2)
            x_hole_indices = np.arange(init_x, n_holes_x, 1)
            x_pos_to_visit = x_positions[x_hole_indices]

            position_xyzrz = etlcontroller.getPositionXYZ()
            etlcontroller.safeMovement(position_xyzrz[0], position_xyzrz[1], init_pos[2], init_pos[3])
            for ix_pos, i_col in zip(x_pos_to_visit, x_hole_indices):
                if i == 1 and i_col == x_hole_indices[0]:
                    init_y = 1
                else:
                    # init_y = max_holes_y - 1
                    init_y = 0

                y_hole_indices = np.arange(init_y, n_holes_y, 1)
                y_pos_to_visit = y_positions[y_hole_indices]

                for iy_pos, i_row in zip(y_pos_to_visit, y_hole_indices):
                    print(f"Col {i_col}, Row {i_row}")
                    x_hole = ix_pos
                    y_hole = iy_pos

                    etlcontroller.safeMovement(x_hole, y_hole, init_pos[2], None)
                    summary, focus_z, fraction = etlcontroller.fullAutoFocus(127, is_double=True)   
                    etlcontroller.changeZ(focus_z)
                    # Take pic
                    position_xyzrz = etlcontroller.getPositionXYZ()
                    position_j1j2j3j4 = etlcontroller.getPositionJ1J2J3_deg()
                    x, y, z, rz = position_xyzrz
                    j1, j2, j3, j4 = position_j1j2j3j4
                    etlcontroller.camera.changeFileName(f"Calibration_27-08-26/picture_col_{i_col}_row{i_row}_iteration{iteration}_X_{x:.3f}Y_{y:.3f}Z_{z:.3f}RZ_{rz:.3f}J1_{j1:.3f}J2_{j2:.3f}J3_{j3:.3f}J4_{j4:.3f}.png")
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
