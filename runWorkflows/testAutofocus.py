from optparse import OptionParser
from matplotlib.image import imread
import matplotlib.pyplot as plt
from CameraClient.RobotCamera import RobotCamera
from RobotBrain.ETLController import ETLController
from RobotBrain.AutoFocusController import AutoFocusController
from ExperimentalSetup.Camera import Camera
from ExperimentalSetup.Robot import Robot
from ExperimentalSetup.Table import Table

import numpy as np

if __name__ == "__main__":
    
    parser = OptionParser(usage="%prog --help")
    parser.add_option("-i", "--ip",              dest="ip",              type='string',  default='192.168.0.189', help="IP of the server.")
    parser.add_option("-p", "--port",            dest="port",            type=int,       default=8080,             help="Port of the server.")
    parser.add_option("-d", "--device",          dest="device",          type='string',  default='/dev/ttyUSB0',     help="Device name")
    parser.add_option("-b", "--bauds",           dest="bauds",           type=int,       default=115200,             help="Bauds")
    parser.add_option("-m", "--move-to-focus", dest="move_to_focus", action="store_true", default=True, help="Move robot to estimated focus at the end.")
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

    robotCamera = RobotCamera(options.ip, options.port, 'picture.png', robot3D)
    etlcontroller = ETLController(options.device, options.bauds, robotCamera, robot3D, False)

    autofocus_velocity = 10.0
    autofocus_range = 10

    autofocus_controller = AutoFocusController(etlcontroller, robotCamera)

    print("Autofocus range:", autofocus_range)
    print("Autofocus velocity:", autofocus_velocity)
    print("Move to focus:", options.move_to_focus)
    # print("Robot initial velocity:", robot_controller.get_velocity())
    print("Robot initial position XYZ:", etlcontroller.getPositionXYZ())
    robotCamera.set_exposure(0.00025)
    
    init_hole_pos = [-72.24, -368.34, 123.51, 140.58]
    step_x = 1.2
    step_y = 1.2
    n_holes_x = 1
    n_holes_y = 1
    for ix in range(n_holes_x):
        for iy in range(n_holes_y):
            print(ix, iy)
            x = init_hole_pos[0] + ix*step_x
            y = init_hole_pos[1] + iy*step_y
            etlcontroller.safeMovement(x, y, init_hole_pos[2], init_hole_pos[3])
            focus_position = (ix, y, init_hole_pos[2], init_hole_pos[3])


            summary, focus_z, fraction = autofocus_controller.start_AutoFocus(
                    focus_position,
                    autofocus_range,
                    autofocus_velocity,
                    move_toFocus=options.move_to_focus,
                    )
            print("Autofocus summary:", summary)
            print("Estimated focus fraction:", fraction)
            print("Estimated focus z:", focus_z)
            print("Robot final velocity:", etlcontroller.get_velocity())
            xf, yf, zf, rzf = etlcontroller.getPositionXYZ()
            robotCamera.changeFileName(f"GluePlate/picture_X{xf}Y{yf}Z{zf}RZ{rzf}.png")
            robotCamera.takePic()
    robot_controller.stop()
