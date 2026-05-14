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

    init_hole_pos = [-72.24, -368.34, 123.51, 140.58]
    step_x = 1.2
    step_y = 1.2
    # Initialize Camera
    robotCamera = RobotCamera(options.ip, options.port, 'picture.png', robot3D)
    
    # Initialize Robot
    etlcontroller = ETLController(options.device, options.bauds, robotCamera, robot3D, False)
    # etlcontroller.camera.set_exposure(0.00025)
    
    # TODO - Define glue plate points position
    init_pos = [-72.24, -368.34, 180, 140.58]
    # # Do 10 photos in the same pos
    # etlcontroller.safeMovement(init_pos[0], init_pos[1], init_pos[2], init_pos[3])
    # summary, focus_z, fraction = etlcontroller.fullAutoFocus(127, is_double=True)   
    # for i in range(10):
    #     etlcontroller.changeZ(180)
    #     etlcontroller.changeZ(focus_z)
    #     position_xyzrz = etlcontroller.getPositionXYZ()
    #     position_j1j2j3j4 = etlcontroller.getPositionJ1J2J3()
    #     x, y, z, rz = position_xyzrz
    #     j1, j2, j3, j4 = position_j1j2j3j4
    #     etlcontroller.camera.changeFileName(f"GluePlate/RepetitivityTest/picture_X_{x:.3f}Y_{y:.3f}Z_{z:.3f}RZ_{rz:.3f}J1_{j1:.3f}J2_{j2:.3f}J3_{j3:.3f}J4_{j4:.3f}_iter{i}.png")
    #     etlcontroller.camera.takePic()
    # Check dead time --> z_range = 0
    # summary, focus_z, fraction = etlcontroller.fullAutoFocus(127, is_double=False)   

    n_holes_x = 10
    n_holes_y = 10
    step_x = 12
    step_y = 12
    
    # etlcontroller.safeMovement(init_pos[0], init_pos[1], init_pos[2], init_pos[3])
    # etlcontroller.safeMovement(init_pos[0]+22*step_x, init_pos[1], init_pos[2], init_pos[3])
    # for ix in range(5, n_holes_x):
    #     for iy in range(n_holes_y):
    #         x_hole = init_pos[0] + ix*step_x
    #         y_hole = init_pos[1] - iy*step_y

    #         etlcontroller.safeMovement(x_hole, y_hole, init_pos[2], init_pos[3])
    #         summary, focus_z, fraction = etlcontroller.fullAutoFocus(127, is_double=True)   
    #         etlcontroller.changeZ(focus_z)
    #         # Take pic
    #         position_xyzrz = etlcontroller.getPositionXYZ()
    #         position_j1j2j3j4 = etlcontroller.getPositionJ1J2J3()
    #         x, y, z, rz = position_xyzrz
    #         j1, j2, j3, j4 = position_j1j2j3j4
    #         etlcontroller.camera.changeFileName(f"GluePlate/DoubleFocus/picture_X_{x:.3f}Y_{y:.3f}Z_{z:.3f}RZ_{rz:.3f}J1_{j1:.3f}J2_{j2:.3f}J3_{j3:.3f}J4_{j4:.3f}.png")
    #         etlcontroller.camera.takePic()
    # Second set of points
    init_pos = [init_pos[0]+step_x*n_holes_x, init_pos[1]-step_y*n_holes_y, init_pos[2], init_pos[3]]
    n_holes_x = 10
    n_holes_y = 10
    step_x = 12
    step_y = 12
    for ix in range(0, n_holes_x):
        for iy in range(n_holes_y):
            x_hole = init_pos[0] + ix*step_x
            y_hole = init_pos[1] - iy*step_y

            etlcontroller.safeMovement(x_hole, y_hole, init_pos[2], init_pos[3])
            summary, focus_z, fraction = etlcontroller.fullAutoFocus(127, is_double=False)   
            etlcontroller.changeZ(focus_z)
            # Take pic
            position_xyzrz = etlcontroller.getPositionXYZ()
            position_j1j2j3j4 = etlcontroller.getPositionJ1J2J3()
            x, y, z, rz = position_xyzrz
            j1, j2, j3, j4 = position_j1j2j3j4
            etlcontroller.camera.changeFileName(f"GluePlate/SingleFocus/picture_X_{x:.3f}Y_{y:.3f}Z_{z:.3f}RZ_{rz:.3f}J1_{j1:.3f}J2_{j2:.3f}J3_{j3:.3f}J4_{j4:.3f}.png")
            etlcontroller.camera.takePic()

    etlcontroller.exit()
