from optparse import OptionParser
from matplotlib.image import imread
import matplotlib.pyplot as plt
import numpy as np
import time
import re

from CameraClient.RobotCamera import RobotCamera
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
#     _______
#    |   |   | 
#    | A | C |
#    |___|___|
#    |   |   |
#    | B | D |
#    |___|___|


## Constants
SAFE_Z = 180
Z_ETROCS = 125 
Z_PCB = 138
Z_COVER = 140 # TODO - Check

def ExtractPosition(name: str):
    pattern = (
        r"X_([-+]?\d*\.?\d+)"
        r"Y_([-+]?\d*\.?\d+)"
        r"Z_([-+]?\d*\.?\d+)"
        r"RZ_([-+]?\d*\.?\d+)"
        r"J1_([-+]?\d*\.?\d+)"
        r"J2_([-+]?\d*\.?\d+)"
        r"J3_([-+]?\d*\.?\d+)"
        r"J4_([-+]?\d*\.?\d+)"
    )

    match = re.search(pattern, name)
    if not match:
        raise ValueError(f"Could not parse positions from: {filename}")

    x, y, z, rz, j1, j2, j3, j4 = map(float, match.groups())

    return {
        "X": x,
        "Y": y,
        "Z": z,
        "RZ": rz,
        "J1": j1,
        "J2": j2,
        "J3": j3,
        "J4": j4,
    }

def TakePicFiducialMarks_ETROC(images, robot):
    """
    """
    center_pos = {}
    corners = []
    # Take pic ETROCs
    for i_image in images:
        pos = ExtractPosition(i_image)
        print(pos)
        x = pos["X"]
        y = pos["Y"]
        z = pos["Z"]
        rz = pos["RZ"]
        j1 = pos["J1"]
        j2 = pos["J2"]
        j3 = pos["J3"]
        # Procces pic and extract center
        p = ProcessFiducialPoint.ProcessFiducialPoint(i_image, is_ETROC=True)
        x_pic, y_pic, valid = p.fit()
        print(f"Position of center: {x_pic}, {y_pic} px")
        # Change from pixels to Robot Coordinates
        # XXX - I need to update robot simulation position
        robot.JMoveRobotTo([j1, j2, z, j4])
        print("After moving the robot")
        x_reco_robot, y_reco_robot, z_reco_robot = robot.cameraProjectionToPoint3D([x_pic, y_pic])
        print(f"Reconstructed position = {x_reco_robot}, {y_reco_robot} mm")
        corners.append([x_reco_robot, y_reco_robot])

    # Compute center position of the ETROC
    print(f"Corners: {corners}")
    corners = np.asarray(corners)
    center = np.mean(corners, axis=0) 
    print(f"Center = {center}")
    # Compute rotation angle
    # Horizontal vectors (C-A and D-B)
    horizontal = ((corners[2]-corners[0]) + (corners[3]-corners[1])) / 2
    theta_rad = np.arctan2(horizontal[1], horizontal[0])
    theta_deg = np.rad2deg(theta_rad)
    center_pos[i_image] = [center[0], center[1], theta_deg]
    print(center_pos)
    return center_pos

def TakePicFiducialMarks_PCB(images, robot):
    """
    """
    center_pos = {}
    corners = []
    # Take pic PCBs
    for i_image in images:
        pos = ExtractPosition(i_image)
        print(pos)
        x = pos["x"]
        y = pos["y"]
        z = pos["z"]
        rz = pos["rz"]
        # Procces pic and extract center
        p = ProcessFiducialPoint.ProcessFiducialPoint(i_image, is_ETROC=True)
        x_pic, y_pic, valid = p.fit()
        # Change from pixels to Robot Coordinates
        # XXX - I need to update robot simulation position
        robot.JMoveRobotTo(position_j1j2j3j4)
        x_reco_robot, y_reco_robot, z_reco_robot = robot.cameraProjectionToPoint3D([x_pic, y_pic])
        print(f"Reconstructed position = {x_reco_robot}, {y_reco_robot}")
        corners.append([x_reco_robot, y_reco_robot])

        # Compute center position of the ETROC
        corners = np.asarray(corners)
        center = np.mean(corners, axis=0) 
        # Compute rotation angle
        # Horizontal vectors (C-A and D-B)
        horizontal = ((corners[2]-corners[0]) + (corners[3]-corners[1])) / 2
        theta_rad = np.arctan2(horizontal[1], horizontal[0])
        theta_deg = np.rad2deg(theta_rad)
        center_pos[i_image] = [center[0], center[1], theta_deg]
    return center_pos

if __name__ == "__main__":
    
    parser = OptionParser(usage="%prog --help")
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

    # Initialize position of assembly parts
    assembly_parts_position = {}

    # Take pictures of the fiducial marks in the ETROCs, compute and store centers
    etroc_images = [
        "FiducialMark/ETROC_1AX_-282.810Y_-347.920Z_158.667RZ_114.610J1_-96.744J2_-90.305J3_158.667J4_72.439.png",
        "FiducialMark/ETROC_1AX_-282.810Y_-367.140Z_158.642RZ_114.610J1_-96.503J2_-85.984J3_158.642J4_67.877.png",
        "FiducialMark/ETROC_1AX_-262.940Y_-347.930Z_158.545RZ_114.610J1_-93.770J2_-93.712J3_158.545J4_72.871.png",
        "FiducialMark/ETROC_1AX_-262.940Y_-367.130Z_158.533RZ_114.600J1_-93.508J2_-89.396J3_158.533J4_68.304.png"
    ]

    etroc_pos = TakePicFiducialMarks_ETROC(etroc_images, robot3D)
    assembly_parts_position.update(etroc_pos)
    # Take pictures of the fiducial marks in the PCB, compute each PCB placement
    # pcb_pos = TakePicFiducialMarks_PCB(pcb_images, robot3D)
    # assembly_parts_position.update(pcb_pos)
