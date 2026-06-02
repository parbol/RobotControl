from optparse import OptionParser
from matplotlib.image import imread
import matplotlib.pyplot as plt
import numpy as np
import json

from CameraClient.RobotCamera import RobotCamera
from RobotBrain.ETLController import ETLController
from ExperimentalSetup.Camera import Camera
from ExperimentalSetup.Robot import Robot
from ExperimentalSetup.Table import Table
import ImageAnalysis.ProcessFiducialPoint as ProcessFiducialPoint

## Geometry and naming scheme
# Up to 4 modules can be done simultaneously, they are called 1, 2, 3 and 4
# Each module contain 4 ETROCs called A, B, C and D
# In all plates the module 1 is the one placed in the most positive y (a.ki.a. closest to the wall or farthest from the user)
# In the tamal plate ETROC A is the one to the most negative x (left position from the user) 
# When the ETROCs are placed on the PCB the position is:
#    A negative x, positive y
#    B negative x, negative y
#    C positive x, positive y
#    D positive x, negative y
#     _______
#    |   |   | 
#    | A | C |
#    |___|___|
#    |   |   |
#    | B | D |
#    |___|___|


## Constants
SAFE_Z = 180
Z_ETROCS = 136 # TODO - Check
Z_PCB = 150 # TODO - Check
Z_COVER = 140 # TODO - Check

def TakePicFiducialMarks_ETROC(modules_to_perform_assembly, etlcontroller):
    """
    Acquire fiducial mark images for ETROCs and compute their center positions
    in robot coordinates.
    IMPORTANT: PICS MUST BE TAKEN IN A, B, C, D ORDER

    Parameters
    ----------
    modules_to_perform_assembly : list[int]
        List of module IDs to process.

    etlcontroller : object

    Returns
    -------
    center_pos : dict
        Dictionary containing computed center positions in robot coordinates.
            center_pos["ETROC_{module}{A|B|C|D}"] = [x, y, rotation]
    """
    with open("FiducialMarkPos.json") as f:
        positions = json.load(f)

    center_pos = {}
    # Take pic ETROCs
    for i_module in modules_to_perform_assembly:
        for i_etroc in ["A", "B", "C", "D"]:
            corners = []
            for i_corner in range(4):
                pos = positions[str(i_module)][f"ETROC_{i_module}{i_etroc}"][i_corner]
                x = pos[0]
                y = pos[1]
                z = pos[2]
                rz = pos[3]
                # Autofocus
                etlcontroller.SafeMovement(x, y, SAFE_Z, rz)
                summary, focus_z, fraction = etlcontroller.fullAutoFocus(z, is_double=True)
                etlcontroller.changeZ(focus_z)
                # Take pic
                position_xyzrz = etlcontroller.getPositionXYZ()
                position_j1j2j3j4 = etlcontroller.getPositionJ1J2J3()
                x_r, y_r, z_r, rz_r = position_xyzrz
                j1_r, j2_r, j3_r, j4_r = position_j1j2j3j4
                image_name = f"FiducialMark/ETROC_{i_module}{i_etroc}X_{x_r:.3f}Y_{y_r:.3f}Z_{z_r:.3f}RZ_{rz_r:.3f}J1_{j1_r:.3f}J2_{j2_r:.3f}J3_{j3_r:.3f}J4_{j4_r:.3f}.png"
                etlcontroller.camera.changeFileName(image_name)
                etlcontroller.camera.takePic()
                # Procces pic and extract center
                p = ProcessFiducialPoint.ProcessFiducialPoint(image_name)
                x_pic, y_pic, d_pic, valid = p.fit()
                # Change from pixels to Robot Coordinates
                x_reco_robot, y_reco_robot, z_reco_robot = etlcontroller.robot.cameraProjectionToPoint3D([x_pic, y_pic])
                corners.append([x_reco_robot, y_reco_robot])

            # Compute center position of the ETROC
            corners = np.asarray(corners)
            center = np.mean(corners, axis=0) 
            # Compute rotation angle
            # Horizontal vectors (C-A and D-B)
            horizontal = ((corners[2]-corners[0]) + (corners[3]-corners[1])) / 2
            theta_rad = np.arctan2(horizontal[1], horizontal[0])
            theta_deg = np.rad2deg(theta_rad)
            center_pos[f"ETROC_{i_module}{i_etroc}"] = [center[0], center[1], theta_deg]
    return center_pos

def TakePicFiducialMarks_PCB(modules_to_perform_assembly, etlcontroller):
    """
    Acquire fiducial mark images for PCBs and compute their center positions 
    in robot coordinates.
    IMPORTANT: PICS MUST BE TAKEN IN A, B, C, D ORDER

    Parameters
    ----------
    modules_to_perform_assembly : list[int]
        List of module IDs to process.

    etlcontroller : object

    Returns
    -------
    center_pos : dict
        Dictionary containing computed center positions in robot coordinates.
            center_pos["PCB_{module}"] = [x, y, rotation]
            center_pos["PCB_{module}{ETROC}"] = [x, y, rotation]
    """
    with open("FiducialMarkPos.json") as f:
        positions = json.load(f)
    center_pos = {}
    # Take pic PCBs
    for i_module in modules_to_perform_assembly:
        corners = []
        for i_corner in range(4):
            pos = positions[str(i_module)][f"PCB_{i_module}"][i_corner]
            x = pos[0]
            y = pos[1]
            z = pos[2]
            rz = pos[3]
            # Autofocus
            etlcontroller.SafeMovement(x, y, SAFE_Z, rz)
            _, focus_z, _ = etlcontroller.fullAutoFocus(z, is_double=True)
            etlcontroller.changeZ(focus_z)
            # Take pic
            position_xyzrz = etlcontroller.getPositionXYZ()
            position_j1j2j3j4 = etlcontroller.getPositionJ1J2J3()
            x_r, y_r, z_r, rz_r = position_xyzrz
            j1_r, j2_r, j3_r, j4_r = position_j1j2j3j4
            image_name = f"FiducialMark/PCB_{i_module}X_{x_r:.3f}Y_{y_r:.3f}Z_{z_r:.3f}RZ_{rz_r:.3f}J1_{j1_r:.3f}J2_{j2_r:.3f}J3_{j3_r:.3f}J4_{j4_r:.3f}.png"
            etlcontroller.camera.changeFileName(image_name)
            etlcontroller.camera.takePic()
            # Procces pic and extract center
            p = ProcessFiducialPoint.ProcessFiducialPoint(image_name)
            x_pic, y_pic, d_pic, valid = p.fit()
            # Change from pixels to Robot Coordinates
            x_reco_robot, y_reco_robot, z_reco_robot = etlcontroller.robot.cameraProjectionToPoint3D([x_pic, y_pic])
            corners.append([x_reco_robot, y_reco_robot])
        # Compute center position of the ETROC
        corners = np.asarray(corners)
        center = np.mean(corners, axis=0)
        # Compute rotation angle
        # Horizontal vectors (C-A and D-B)
        horizontal = ((corners[2]-corners[0]) + (corners[3]-corners[1])) / 2
        theta_rad = np.arctan2(horizontal[1], horizontal[0])
        theta_deg = np.rad2deg(theta_rad)
        center_pos[f"PCB_{i_module}"] = [center[0], center[1], theta_deg]
        # Compute placement of each module in the PCB
        # the placement is the mean position between the corner and the center
        # XXX - Assuming pics are taken in A -> B -> C -> D order
        for i, i_etroc in enumerate(["A", "B", "C", "D"]):
            placement_position = (center + corners[i])/2
            center_pos[f"PCB_{i_module}{i_etroc}"] = [placement_position[0], placement_position[1], theta_deg] 

    return center_pos


if __name__ == "__main__":
    
    parser = OptionParser(usage="%prog --help")
    parser.add_option("-i", "--ip", dest="ip", type="string", default="192.168.0.189", help="IP of the camera server.")
    parser.add_option("-p", "--port", dest="port", type=int, default=8080, help="Port of the camera server.")
    parser.add_option("-d", "--device", dest="device", type="string", default="/dev/ttyUSB0", help="Robot device name.")
    parser.add_option("-b", "--bauds", dest="bauds", type=int, default=115200, help="Robot bauds.")
    (options, args) = parser.parse_args()

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

    ################ Initialize 3D setup model
    # The table
    table = Table(0.01, 0.0)
    # Get Calibration
    calibrationHandler = calibrationHandler()
    cali = calibrationHandler.getLastCalibration()

    # The physical camera
    camera = Camera(x = cali['cameraX'], y = cali['cameraY'],
                    z = cali['cameraZ'], psi = cali['cameraPsi'],
                    theta = cali['cameraTheta'], phi = cali['cameraPhi'],
                    cx = cali['c'], cy = cali['c'],
                    focaldistance = cali['focaldistance'],
                    focusdistance = cali['focusdistance'])
    # The 3D model of the robot
    robot3D =  Robot(cali['R1'], cali['R2'], cali['Z0'], table, camera, fig, ax1, ax2, ax3)
    ################ END - Initialize 3D setup model

    # Initialize Camera
    robotCamera = RobotCamera(options.ip, options.port, 'picture.png', robot3D)
    
    # Initialize Robot
    etlcontroller = ETLController(options.device, options.bauds, robotCamera, robot3D, False)

    # Initialize position of assembly parts
    assembly_parts_position = {}

    modules_to_perform_assembly = [1, 2, 3, 4]
    # Take pictures of the fiducial marks in the ETROCs, compute and store centers
    etroc_pos = TakePicFiducialMarks(modules_to_perform_assembly, etlcontroller, is_etroc=True)
    assembly_parts_position.update(etroc_pos)
    # Take pictures of the fiducial marks in the PCB, compute each PCB placement
    pcb_pos = TakePicFiducialMarks(modules_to_perform_assembly, etlcontroller, is_etroc=False)
    assembly_parts_position.update(pcb_pos)

    # Do assembly
    # Grab picker tool if not already
    # TODO
    for i_module in modules_to_perform_assembly:
        for i_etroc in ["A", "B", "C", "D"]:
            # Pick ETROC, assume orientation is ok (apart from correction)
            etroc_pos = assembly_parts_position[f"ETROC_{i_module}{i_etroc}"]
            etlcontroller.grabAssemblyPart(etroc_pos[0], etroc_pos[1], Z_ETROCS, etroc_pos[2], f"ETROC_{i_module}{i_etroc}")
            # Release ETROC in PCB, 1.- Move to position and apply correction angle 2.- Release
            release_pos = assembly_parts_position[f"PCB_{i_module}{i_etroc}"]
            etlcontroller.releaseAssemblyPart(release_pos[0], release_pos[1], Z_PCB, release_pos[2], f"PCB_{i_module}{i_etroc}")
    
    # Now 4 ETROCs are in each PCB
    # Put the cover plate on top but I do not have any fiducial mark

    # Close connection
    etlcontroller.exit()
