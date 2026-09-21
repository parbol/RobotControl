from optparse import OptionParser
import numpy as np
import json
from datetime import datetime
import os

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

now = datetime.now()
date_str = f"{now.year}-{now.month}-{now.day}-{now.hour}"
PATH= f"../FiducialETROCs_{date_str}"
os.makedirs(PATH, exist_ok=True)

def load_assembly_positions(path):
    """
    Load a previously saved assembly positions file, skipping the fiducial
    imaging phase entirely (e.g. to retry the physical assembly after a
    failed run without re-measuring).
    """
    with open(path) as f:
        assembly_parts_position = json.load(f)
    print(f"Assembly positions loaded from {path}")
    return assembly_parts_position



if __name__ == "__main__":
    
    parser = OptionParser(usage="%prog --help")
    parser.add_option("-d", "--device", dest="device", type="string", default="/dev/ttyUSB0", help="Robot device name.")
    parser.add_option("-b", "--bauds", dest="bauds", type=int, default=115200, help="Robot bauds.")
    parser.add_option("-c", "--calibration", dest="calibration", type=str, default="ExperimentalSetup/Calibrations/calibrations.txt", help="Robot calibration file.")
    parser.add_option("--pos", "--position", dest="position", type=str, default=PATH, help="Json with assembly parts position.")
    # parser.add_option("-cor", "--correction", dest="correction", type=str, default=None, help="Json file with per hybrid correction")
    (options, args) = parser.parse_args()

    ################ Initialize 3D setup model
    # The table
    table = Table(0.01, 0.0)
    # Get Calibration
    calibrationHandler = CalibrationHandler(name=options.calibration)
    cali = calibrationHandler.getLastCalibration()

    # The physical camera
    camera = Camera(x = cali['cameraX'], y = cali['cameraY'],
                    z = cali['cameraZ'], psi = cali['cameraPsi'],
                    theta = cali['cameraTheta'], phi = cali['cameraPhi'],
                    cx = cali['c'], cy = cali['c'],
                    focaldistance = cali['focaldistance'],
                    focusdistance = cali['focusdistance'])
    # The 3D model of the robot
    robot3D =  Robot(R1=cali['R1'], R2=cali['R2'], Z0=cali['Z0'], phiOrig=cali['phiOrig'], table=table, camera=camera)
    ################ END - Initialize 3D setup model

    ################ Initialize Connections
    # Initialize Robot
    etlcontroller = ETLController(options.device, options.bauds, None, robot3D, False)
    ############### END - Initialize Connections

    try:
        ################ Assembly
        assembly_parts_position = load_assembly_positions(options.position)

        # modules_to_perform_assembly = [1, 2, 3, 4]
        modules_to_perform_assembly = [1]
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

    finally:
        # Release picker tool if not already
        etlcontroller.releasePickerTool()
        ################ END -Assembly
        # Close connection
        etlcontroller.exit()
