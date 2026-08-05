from optparse import OptionParser
from matplotlib.image import imread
import matplotlib.pyplot as plt
import numpy as np
import json
import time

from CameraClient.RobotCamera import RobotCamera
from RobotBrain.ETLController import ETLController
from ExperimentalSetup.Camera import Camera
from ExperimentalSetup.Robot import Robot
from ExperimentalSetup.Table import Table
from ExperimentalSetup.CalibrationHandler import CalibrationHandler
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
#     ___________
#    |     |     | 
#    |  A  |  C  |
#    |_____|_____|
#    |     |     |
#    |  B  |  D  |
#    |_____|_____|


## Constants
SAFE_Z = 180
Z_ETROCS = 125 
Z_PCB = 138
Z_COVER = 140 # TODO - Check

# Units
mm = 1

# Corrections
ETROC_CENTER_CORRECTION = [0.748*mm, 0.0*mm]
PCB_SHIFT_POS = [2.294*mm, 2.499*mm]
ETROC_SIZE = [23*mm, 21*mm]

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
    with open("runWorkflows/FiducialMarkPos.json") as f:
        positions = json.load(f)

    center_pos = {}
    # Take pic ETROCs
    for i_module in modules_to_perform_assembly:
        # for i_etroc in ["A", "B", "C", "D"]:
        for i_etroc in ["A"]:
            corners = []
            print("*"*20)
            print(f" Module {i_module}")
            print(f" ETROC {i_etroc}")
            print("*"*20)
            for i_corner in range(4):
                pos = positions[str(i_module)][f"ETROC_{i_module}{i_etroc}"][i_corner]
                print(pos)
                x = pos["x"]
                y = pos["y"]
                z = pos["z"]
                rz = pos["rz"]
                # Autofocus
                print(f"Photo position = {x}, {y}, {z}, {rz}")
                etlcontroller.safeMovement(x, y, SAFE_Z, rz)
                summary, focus_z, fraction = etlcontroller.fullAutoFocus(z, is_double=True)
                etlcontroller.changeZ(focus_z)
                # Take pic
                position_xyzrz = etlcontroller.getPositionXYZ()
                position_j1j2j3j4_rad = etlcontroller.getPositionJ1J2J3_rad()
                position_j1j2j3j4_deg = etlcontroller.getPositionJ1J2J3_deg()
                x_r, y_r, z_r, rz_r = position_xyzrz
                j1_r, j2_r, j3_r, j4_r = position_j1j2j3j4_deg
                image_name = f"FiducialMark/ETROC_{i_module}{i_etroc}X_{x_r:.3f}Y_{y_r:.3f}Z_{z_r:.3f}RZ_{rz_r:.3f}J1_{j1_r:.3f}J2_{j2_r:.3f}J3_{j3_r:.3f}J4_{j4_r:.3f}.png"
                etlcontroller.camera.changeFileName(image_name)
                etlcontroller.camera.takePic()
                # Procces pic and extract center
                p = ProcessFiducialPoint.ProcessFiducialPoint(image_name, is_ETROC=True)
                x_pic, y_pic, valid = p.fit()
                # Change from pixels to Robot Coordinates
                # XXX - I need to update robot simulation position
                etlcontroller.robot.JMoveRobotTo(position_j1j2j3j4_rad)
                x_reco_robot, y_reco_robot, z_reco_robot = etlcontroller.robot.cameraProjectionToPoint3D([x_pic, y_pic])
                print(f"Reconstructed position = {x_reco_robot}, {y_reco_robot}")
                corners.append([x_reco_robot, y_reco_robot])

            # Compute center position of the ETROC
            corners = np.asarray(corners)
            center = np.mean(corners, axis=0) 
            # Correct center position with nominal fiducial marks pos, I assume pads are placed up (positive y)
            if i_module == "A" or i_module == "B":
                # Pads in negative X 
                center = [center[0]-ETROC_CENTER_CORRECTION[0], center[1]+ETROC_CENTER_CORRECTION[1]]
            if i_module == "C" or i_module == "D":
                # Pads in positive X 
                center = [center[0]+ETROC_CENTER_CORRECTION[0], center[1]+ETROC_CENTER_CORRECTION[1]]
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
    with open("runWorkflows/FiducialMarkPos.json") as f:
        positions = json.load(f)
    place_pos = {}
    # Take pic PCBs
    for i_module in modules_to_perform_assembly:
        corners = []
        for i_corner in range(4):
            pos = positions[str(i_module)][f"PCB_{i_module}"][i_corner]
            x = pos["x"]
            y = pos["y"]
            z = pos["z"]
            rz = pos["rz"]
            # Autofocus
            etlcontroller.safeMovement(x, y, SAFE_Z, rz)
            _, focus_z, _ = etlcontroller.fullAutoFocus(z, is_double=True)
            etlcontroller.changeZ(focus_z)
            # Take pic
            position_xyzrz = etlcontroller.getPositionXYZ()
            position_j1j2j3j4_rad = etlcontroller.getPositionJ1J2J3_rad()
            position_j1j2j3j4_deg = etlcontroller.getPositionJ1J2J3_deg()
            x_r, y_r, z_r, rz_r = position_xyzrz
            j1_r, j2_r, j3_r, j4_r = position_j1j2j3j4_deg
            image_name = f"FiducialMark/PCB_{i_module}X_{x_r:.3f}Y_{y_r:.3f}Z_{z_r:.3f}RZ_{rz_r:.3f}J1_{j1_r:.3f}J2_{j2_r:.3f}J3_{j3_r:.3f}J4_{j4_r:.3f}.png"
            etlcontroller.camera.changeFileName(image_name)
            etlcontroller.camera.takePic()
            # Procces pic and extract center
            p = ProcessFiducialPoint.ProcessFiducialPoint(image_name, is_ETROC=False)
            x_pic, y_pic, valid = p.fit()
            # Change from pixels to Robot Coordinates
            etlcontroller.robot.JMoveRobotTo(position_j1j2j3j4_rad)
            x_reco_robot, y_reco_robot, z_reco_robot = etlcontroller.robot.cameraProjectionToPoint3D([x_pic, y_pic])
            print(f"Reconstructed position = {x_reco_robot}, {y_reco_robot}")
            corners.append([x_reco_robot, y_reco_robot])
        # Compute center position of the ETROC
        corners = np.asarray(corners)
        # center = np.mean(corners, axis=0)
        # Compute rotation angle
        # Horizontal vectors (C-A and D-B)
        horizontal = ((corners[2]-corners[0]) + (corners[3]-corners[1])) / 2
        theta_rad = np.arctan2(horizontal[1], horizontal[0])
        theta_deg = np.rad2deg(theta_rad)
        # center_pos[f"PCB_{i_module}"] = [center[0], center[1], theta_deg]
        # Compute placement of each module in the PCB
        # the placement is the mean position between the corner and the center
        # XXX - Assuming pics are taken in A -> B -> C -> D order
        place_pos[f"PCB_{i_module}A"] = [
                corners[0, 0] - PCB_SHIFT_POS[0] + ETROC_SIZE[0]/2,
                corners[0, 1] - PCB_SHIFT_POS[1] - ETROC_SIZE[1]/2, theta_deg
                ]
        place_pos[f"PCB_{i_module}B"] = [
                corners[1, 0] - PCB_SHIFT_POS[0] + ETROC_SIZE[0]/2,
                corners[1, 1] + PCB_SHIFT_POS[1] + ETROC_SIZE[1]/2, theta_deg
                ]
        place_pos[f"PCB_{i_module}C"] = [
                corners[2, 0] + PCB_SHIFT_POS[0] - ETROC_SIZE[0]/2,
                corners[2, 1] - PCB_SHIFT_POS[1] - ETROC_SIZE[1]/2, theta_deg
                ]
        place_pos[f"PCB_{i_module}D"] = [
                corners[3, 0] + PCB_SHIFT_POS[0] - ETROC_SIZE[0]/2,
                corners[3, 1] + PCB_SHIFT_POS[1] + ETROC_SIZE[1]/2, theta_deg
                ]

    return place_pos


if __name__ == "__main__":
    
    parser = OptionParser(usage="%prog --help")
    parser.add_option("-i", "--ip", dest="ip", type="string", default="192.168.0.189", help="IP of the camera server.")
    parser.add_option("-p", "--port", dest="port", type=int, default=8080, help="Port of the camera server.")
    parser.add_option("-d", "--device", dest="device", type="string", default="/dev/ttyUSB0", help="Robot device name.")
    parser.add_option("-b", "--bauds", dest="bauds", type=int, default=115200, help="Robot bauds.")
    (options, args) = parser.parse_args()

    ################ Initialize 3D setup model
    # The table
    table = Table(0.01, 0.0)
    # Get Calibration
    calibrationHandler = CalibrationHandler(name="ExperimentalSetup/Calibrations/calibrations.txt")
    cali = calibrationHandler.getLastCalibration()

    # The physical camera
    camera = Camera(x = cali['cameraX'], y = cali['cameraY'],
                    z = cali['cameraZ'], psi = cali['cameraPsi'],
                    theta = cali['cameraTheta'], phi = cali['cameraPhi'],
                    cx = cali['c'], cy = cali['c'],
                    focaldistance = cali['focaldistance'],
                    focusdistance = cali['focusdistance'])
    # The 3D model of the robot
    robot3D =  Robot(cali['R1'], cali['R2'], cali['Z0'], table, camera)
    ################ END - Initialize 3D setup model

    # Initialize Camera
    robotCamera = RobotCamera(options.ip, options.port, 'picture.png', robot3D)
    
    # Initialize Robot
    etlcontroller = ETLController(options.device, options.bauds, robotCamera, robot3D, False)

    # Initialize position of assembly parts
    assembly_parts_position = {}

    # modules_to_perform_assembly = [1, 2, 3, 4]
    modules_to_perform_assembly = [1]
    # Take pictures of the fiducial marks in the ETROCs, compute and store centers
    etroc_pos = TakePicFiducialMarks_ETROC(modules_to_perform_assembly, etlcontroller)
    assembly_parts_position.update(etroc_pos)
    # Take pictures of the fiducial marks in the PCB, compute each PCB placement
    pcb_pos = TakePicFiducialMarks_PCB(modules_to_perform_assembly, etlcontroller)
    assembly_parts_position.update(pcb_pos)

    # Do assembly
    # Grab picker tool if not already
    etlcontroller.grabPickerTool()
    # TODO
    for i_module in modules_to_perform_assembly:
        # for i_etroc in ["A", "B", "C", "D"]:
        for i_etroc in ["A"]:
            # Pick ETROC, assume orientation is ok (apart from correction)
            etroc_pos = assembly_parts_position[f"ETROC_{i_module}{i_etroc}"]
            print(f"Moving to grab ETROC from {etroc_pos}")
            etlcontroller.grabAssemblyPart(etroc_pos[0], etroc_pos[1], Z_ETROCS, etroc_pos[2], f"ETROC_{i_module}{i_etroc}")
            # Release ETROC in PCB, 1.- Move to position and apply correction angle 2.- Release
            release_pos = assembly_parts_position[f"PCB_{i_module}{i_etroc}"]
            print(f"Moving to release ETROC at {release_pos}")
            etlcontroller.releaseAssemblyPart(release_pos[0], release_pos[1], Z_PCB, release_pos[2], f"PCB_{i_module}{i_etroc}")
    
    # Now 4 ETROCs are in each PCB
    # Put the cover plate on top but I do not have any fiducial mark

    # Release picker tool if not already
    etlcontroller.releasePickerTool()
    # Close connection
    etlcontroller.exit()
