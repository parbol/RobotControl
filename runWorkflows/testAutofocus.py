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

    # Initialize Camera
    robotCamera = RobotCamera(options.ip, options.port, 'picture.png', robot3D)
    
    # Initialize Robot
    etlcontroller = ETLController(options.device, options.bauds, robotCamera, robot3D, False)

    focus_position = (434.815, -147.438, 127.388, -72.23)
    autofocus_velocity = 10.0
    autofocus_range = 1.0

    autofocus_controller = AutoFocusController(etlcontroller)

    print("Autofocus input position:", focus_position)
    print("Autofocus range:", autofocus_range)
    print("Autofocus velocity:", autofocus_velocity)
    print("Move to focus:", options.move_to_focus)
    print("Robot initial velocity:", robot_controller.get_velocity())
    print("Robot initial position XYZ:", robot_controller.getPositionXYZ())

    try:
        robot_camera.set_exposure(0.00025)

        summary, focus_z, fraction = autofocus_controller.start_AutoFocus(
            focus_position,
            autofocus_range,
            autofocus_velocity,
            move_toFocus=options.move_to_focus,
        )

        print("Autofocus summary:", summary)
        print("Estimated focus fraction:", fraction)
        print("Estimated focus z:", focus_z)
        print("Robot final velocity:", robot_controller.get_velocity())
        print("Robot final position XYZ:", robot_controller.getPositionXYZ())
        robot_camera.changeFileName("runWorkflows/picture_finalFocus.png")
        robot_camera.takePic()
        print("Final focus picture saved to:", "runWorkflows/picture_finalFocus.png")
    finally:
        robot_controller.stop()
