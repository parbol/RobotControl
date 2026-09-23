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

def DebugPlot(corners, photo, center, real_center=None):

    # Debug plot
    corners_arr = np.asarray(corners)
    photo_arr = np.asarray(photo)
    
    plt.figure(figsize=(6, 6))
    
    # Fiducial positions reconstructed in robot coordinates
    plt.scatter(corners_arr[:, 0], corners_arr[:, 1], marker="o", s=100, label="Corners")
    
    # Robot positions where photos were taken
    plt.scatter(photo_arr[:, 0], photo_arr[:, 1], marker="x", s=100, label="Photo positions")
    
    # Label points
    for i, (x, y) in enumerate(corners_arr):
        plt.annotate(f"C{i}", (x, y))
    
    for i, (x, y) in enumerate(photo_arr):
        plt.annotate(f"P{i}", (x, y))
    
    # Center
    plt.scatter(center[0], center[1], marker="*", s=300, label="Center")
   
    # Real center
    if real_center is not None:
        plt.scatter(real_center[0], real_center[1], marker="v", s=150, label = "Real center")

    plt.axis("equal")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend()
    plt.xlabel("X [mm]")
    plt.ylabel("Y [mm]")
    
    plt.show()

def TakePicFiducialMarks_ETROC(images, robot):
    """
    """
    robot.JMoveRobotTo([0,0,180,0])
    _ = robot.cameraProjectionToPoint3D([0,0])
    center_pos = {}
    corners = []
    photo_pos = []
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
        j4 = pos["J4"]
        # Procces pic and extract center
        p = ProcessFiducialPoint.ProcessFiducialPoint(i_image, is_ETROC=True)
        x_pic, y_pic, valid = p.fit()
        print(f"Position of center: {x_pic}, {y_pic} px")
        # Change from pixels to Robot Coordinates
        robot.JMoveRobotTo([np.radians(j1), np.radians(j2), j3, np.radians(j4)])
        print("After moving the robot")
        x_reco_robot, y_reco_robot, z_reco_robot = robot.cameraProjectionToPoint3D([x_pic, y_pic])
        print(f"Reconstructed position = {x_reco_robot}, {y_reco_robot} mm")
        corners.append([x_reco_robot, y_reco_robot])
        photo_pos.append([x, y])

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
    DebugPlot(corners, photo_pos, center, real_center=[-358.57, -315.35])
    return center_pos

def TakePicFiducialMarks_PCB(images, robot):
    """
    """
    center_pos = {}
    corners = []
    photo_pos = []
    # Take pic PCBs
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
        j4 = pos["J4"]
        # Procces pic and extract center
        p = ProcessFiducialPoint.ProcessFiducialPoint(i_image, is_ETROC=True)
        x_pic, y_pic, valid = p.fit()
        # Change from pixels to Robot Coordinates
        robot.JMoveRobotTo([np.radians(j1), np.radians(j2), j3, np.radians(j4)])
        x_reco_robot, y_reco_robot, z_reco_robot = robot.cameraProjectionToPoint3D([x_pic, y_pic])
        print(f"Reconstructed position = {x_reco_robot}, {y_reco_robot}")
        corners.append([x_reco_robot, y_reco_robot])
        photo_pos.append([x, y])

    # Compute center position of the ETROC
    corners = np.asarray(corners)
    center = np.mean(corners, axis=0) 
    # Compute rotation angle
    # Horizontal vectors (C-A and D-B)
    horizontal = ((corners[2]-corners[0]) + (corners[3]-corners[1])) / 2
    theta_rad = np.arctan2(horizontal[1], horizontal[0])
    theta_deg = np.rad2deg(theta_rad)
    center_pos[i_image] = [center[0], center[1], theta_deg]

    DebugPlot(corners, photo_pos, center)
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
    print(f"Calibration values: ")
    print(f" cameraX = {cali['cameraX']}")
    print(f" cameraY = {cali['cameraY']}")
    print(f" cameraZ = {cali['cameraZ']}")
    print(f" cameraPsi = {cali['cameraPsi']}")
    print(f" cameraPhi = {cali['cameraPhi']}")
    print(f" cameraTheta = {cali['cameraTheta']}")
    print(f" c = {cali['c']}")
    print(f" focusdistance = {cali['focusdistance']}")
    print(f" focaldistance = {cali['focaldistance']}")

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
    pcb_images = [
        "FiducialMark/PCB_1X_353.350Y_-374.330Z_173.659RZ_107.040J1_-20.703J2_-69.801J3_173.659J4_-16.536.png",
        "FiducialMark/PCB_1X_353.630Y_-335.130Z_173.846RZ_107.020J1_-14.563J2_-78.820J3_173.846J4_-13.637.png",
        "FiducialMark/PCB_1X_406.730Y_-375.120Z_173.849RZ_107.030J1_-21.824J2_-55.182J3_173.849J4_-30.024.png",
        "FiducialMark/PCB_1X_407.120Y_-335.970Z_174.160RZ_107.050J1_-15.162J2_-65.160J3_174.160J4_-26.728.png"
    ]
    pcb_pos = TakePicFiducialMarks_PCB(pcb_images, robot3D)
    assembly_parts_position.update(pcb_pos)
    print(assembly_parts_position)
