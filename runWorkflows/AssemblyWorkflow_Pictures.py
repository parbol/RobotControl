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
#         x' →
#     ┌────────┐  0.2  ┌────────┐
#     │        │   mm  │        │
#     │   A    │───────│   C    │
#     │        │       │        │
#     └────────┘       └────────┘
#        │
#       0.2 mm
#        │
#     ┌────────┐       ┌────────┐
#     │        │       │        │
#     │   B    │       │   D    │
#     │        │       │        │
#     └────────┘       └────────┘

## Constants
SAFE_Z = 180

# Units
mm = 1

# Corrections
# ETROC_CENTER_CORRECTION = [0.748*mm, 0.00*mm]
ETROC_CENTER_CORRECTION = [0.778*mm, 0.04*mm]
# PCB_SHIFT_POS = [2.294*mm, 2.499*mm]
# PCB_SHIFT_POS = [2.42*mm, 2.48*mm]
ETROC_SIZE = [23*mm, 21*mm]
ETROC_GAP = 0.2*mm
# CORRECTION = [0*mm, -0.5*mm]
CORRECTION = [0*mm, 0*mm]

now = datetime.now()
date_str = f"{now.year}-{now.month}-{now.day}-{now.hour}"
PATH= f"../FiducialETROCs_{date_str}"
os.makedirs(PATH, exist_ok=True)

def run_retakes(retake, etlcontroller, fiducial):
    """
    Execute picture retakes
    """
    single_retake = retake.split(",")
    results = {}

    for i_single_retake in single_retake:
        parts = i_single_retake.split(":")

        if parts[0] == "ETROC" and len(parts)==4:
            _, module, letter, corner = parts
            results[i_single_retake] = RetakeFiducialCorner_ETROC(int(module), letter, int(corner), etlcontroller, fiducial)

        elif parts[0] == "PCB" and len(parts)==3:
            _, module, corner = parts
            results[i_single_retake] = RetakeFiducialCorner_PCB(int(module), int(corner), etlcontroller, fiducial)

        else:
            raise ValueError(f"Not valid format for retake: {i_single_retake}. It should be 'ETROC:<Module>:<Letter>:<Corner>' or 'PCB:<Module>:<Corner>'")

    return results

def _load_corners_json(folder_name):
    path = f"{folder_name}/_raw_corners.json"
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}

def _save_corners_json(folder_name, data, name, corners):
    """
    Save into a json file the position of the corners and the distances between them
    Parameters
    ----------
    folder_name : str 
        Folder where the JSON file is stored
    data : dict 
        Dictionary containing the previously stored corner positions and distances
    name : str 
        Name used to identify the set of corners in the JSON file 
    corners : array-like 
        Array containing the [x, y] positions of the four corners.
    """

    path = f"{folder_name}/_raw_corners.json"

    data[name] = corners
    data[f"{name}_distances"] = _compute_corner_distances(corners)

    with open(path, "w") as f:
        json.dump(data, f, indent=4)

def _compute_corner_distances(corners):
    corners = np.asarray(corners, dtype=float)

    pairs = {
        "0-1": (0, 1),
        "1-2": (1, 2),
        "2-3": (2, 3),
        "3-0": (3, 0),
        "0-2": (0, 2),
        "1-3": (1, 3),
    }

    distances = {}

    for name, (i, j) in pairs.items():
        vector = corners[j] - corners[i]

        distances[name] = {
            "dx": float(vector[0]),
            "dy": float(vector[1]),
            "distance": float(np.linalg.norm(vector))
        }

    return distances

def _corners_all_valid(corners):
    """
    Return True if 4 corners are valid pics
    """
    return all(c is not None and c[0] is not None and c[1] is not None for c in corners)

def _update_assembly_positions_file(key, value, path=None):
    """
    Patch a single key inside the final assembly_positions.json, without
    touching the rest of the file. If the file does not exist yet, nothing
    is written to disk (the caller still gets the recomputed value back).
    """
    path = path or f"{PATH}/assembly_positions.json"
    if not os.path.exists(path):
        print(f"No existe todavia {path}; no se ha actualizado nada en disco, "
              f"solo se devuelve el valor recalculado de {key}.")
        return
    with open(path) as f:
        data = json.load(f)
    data[key] = value
    with open(path, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Actualizado {key} en {path}")


def RetakeFiducialCorner_ETROC(module: int, letter: str, corner: int, etlcontroller, fiducial):
    """
    Repeats a single corner and recomputes the center and rotation of this ETROC

    Parameters
    ----------
    module : int
        Module number (1, 2, 3 o 4).
    etroc_letter : str
        "A", "B", "C" o "D".
    corner_index : int
        Index of the corner to repeat (0, 1, 2 o 3).
    etlcontroller : object
    fiducial : str
        File with fiducial marks positions.

    Returns
    ----------
    list[float] | None
        [x, y, rotation] recomputed from new pic or None if not valid photo
    """

    with open(fiducial) as f:
        positions = json.load(f)

    folder_name = f"{PATH}/FiducialETROCs"
    part_name = f"ETROC_{module}{letter}"

    raw_corners = _load_corners_json(folder_name)
    if part_name not in raw_corners:
        raise RuntimeError(f"No previous corner saved for {part_name}; you need to run first the whole pictures")

    pos = positions[str(module)][part_name][corner]
    print(f"Repeating conrner {corner} of {part_name}")
    new_corner, valid = _locate_fiducial(etlcontroller, pos, folder_name=folder_name, part_name=part_name, is_ETROC=True)
    if not valid:
        print("Not valid pic.")
        return None

    raw_corners[part_name][corner] = new_corner
    _save_corners_json(folder_name, raw_corners, part_name, raw_corners[part_name])

    if not _corners_all_valid(raw_corners[part_name]):
        pending = [i for i, c in enumerate(raw_corners[part_name])
                   if c is None or c[0] is None or c[1] is None]
        print(f"Corner {corner} of {part_name} saved, but you still need to retake {pending}; center not recomputed")
        return None

    # Recompute center
    result = ComputeCenter_ETROC(np.asarray(raw_corners[part_name]), letter)
    _update_assembly_positions_file(part_name, result)
    return result

def ComputeCenter_ETROC(corners: np.array, etroc_letter):
    """
    Robot reference frame --> x,y
    ETROC reference frame --> x',y'
    """
    # In x,y
    center = np.mean(corners, axis=0)

    # ETROC orientation 
    horizontal = ((corners[2] - corners[0]) + (corners[3] - corners[1])) / 2
    theta_rad = np.arctan2(horizontal[1], horizontal[0])
    theta_deg = np.rad2deg(theta_rad)

    # Correction defined in ETROC reference frame (x', y')
    correction = np.array(ETROC_CENTER_CORRECTION, dtype=float)
    # A/B and C/D have opposite correction directions
    if etroc_letter not in ("A", "B"):
        correction = -correction

    # Rotate correction from ETROC frame (x', y') to robot frame (x, y)
    rotation = np.array([
        [np.cos(theta_rad), -np.sin(theta_rad)],
        [np.sin(theta_rad),  np.cos(theta_rad)]
    ])
    correction_robot = rotation @ correction

    # Apply correction in robot reference frame
    center = center + correction_robot


    return [center[0], center[1], theta_deg]

def TakePicFiducialMarks_ETROC(modules_to_perform_assembly, etlcontroller, fiducial):
    """
    Acquire fiducial mark images for ETROCs and compute their center positions
    in robot coordinates.
    IMPORTANT: PICS MUST BE TAKEN IN A, B, C, D ORDER

    Parameters
    ----------
    modules_to_perform_assembly : list[int]
        List of module IDs to process.

    etlcontroller : object
    
    fiducial: str
        Name of the file with the fiducial positions

    Returns
    -------
    center_pos : dict
        Dictionary containing computed center positions in robot coordinates.
            center_pos["ETROC_{module}{A|B|C|D}"] = [x, y, rotation]
    """
    with open(fiducial) as f:
        positions = json.load(f)

    # Folder to store images
    folder_name = f"{PATH}/FiducialETROCs"
    os.makedirs(folder_name, exist_ok=True)

    center_pos = {}
    # Take pic ETROCs
    for i_module in modules_to_perform_assembly:
        #for i_etroc in ["A", "B", "C", "D"]:
        for i_etroc in ["A"]:
            corners = []
            print("*"*20)
            print(f" Module {i_module}")
            print(f" ETROC {i_etroc}")
            print("*"*20)
            valid = True
            for i_corner in range(4):
                pos = positions[str(i_module)][f"ETROC_{i_module}{i_etroc}"][i_corner]
                print(i_corner, pos)
                corner, i_valid = _locate_fiducial(etlcontroller, pos, folder_name=folder_name, part_name=f"ETROC_{i_module}{i_etroc}", is_ETROC=True)
                valid = valid and i_valid
                corners.append(corner)

            # Store raw corners
            raw_corners = _load_corners_json(folder_name)
            _save_corners_json(folder_name, raw_corners, f"ETROC_{i_module}{i_etroc}", corners)

            if valid:
                # Compute center position of the ETROC
                result = ComputeCenter_ETROC(np.asarray(corners), i_etroc)
                center_pos[f"ETROC_{i_module}{i_etroc}"] = result
            else:
                center_pos[f"ETROC_{i_module}{i_etroc}"] = [None, None, None]
    return center_pos

def RetakeFiducialCorner_PCB(module: int, corner: int, etlcontroller, fiducial):
    """
    Repeats a single corner and recomputes placement position and rotation of this PCB

    Parameters
    ----------
    module : int
        Module number (1, 2, 3 o 4).
    corner_index : int
        Index of the corner to repeat (0, 1, 2 o 3).
    etlcontroller : object
    fiducial : str
        File with fiducial marks positions.

    Returns
    ----------
    dict | None
        {"PCB_moduleA: [x, y, rotation],...} recomputed from new pic or None if not valid photo
    """

    with open(fiducial) as f:
        positions = json.load(f)

    folder_name = f"{PATH}/FiducialPCB"
    part_name = f"PCB_{module}"

    raw_corners = _load_corners_json(folder_name)
    if part_name not in raw_corners:
        raise RuntimeError(f"No previous corner saved for {part_name}; you need to run first the whole pictures")

    pos = positions[str(module)][part_name][corner]
    print(f"Repeating corner {corner} of {part_name}")
    new_corner, valid = _locate_fiducial(etlcontroller, pos, folder_name=folder_name, part_name=part_name, is_ETROC=False)
    if not valid:
        print("Not valid pic.")
        return None

    raw_corners[part_name][corner] = new_corner
    _save_corners_json(folder_name, raw_corners, part_name, raw_corners[part_name])

    if not _corners_all_valid(raw_corners[part_name]):
        pending = [i for i, c in enumerate(raw_corners[part_name])
                   if c is None or c[0] is None or c[1] is None]
        print(f"Corner {corner} of {part_name} saved, but you still need to retake {pending}; placement not recomputed")
        return None

    # Recompute placement
    result = ComputePlacement_PCB(np.asarray(raw_corners[part_name]), module)
    for key, value in result.items():
        _update_assembly_positions_file(key, value)
    return result

def ComputePlacement_PCB(corners: np.array, module):
    place_pos = {}

    # Center in robot coordinates
    pcb_center = np.mean(corners, axis=0)
    horizontal = ((corners[2]-corners[0]) + (corners[3]-corners[1])) / 2
    theta_rad = np.arctan2(horizontal[1], horizontal[0])
    theta_deg = np.rad2deg(theta_rad)

    rotation = np.array([
        [np.cos(theta_rad), -np.sin(theta_rad)],
        [np.sin(theta_rad), np.cos(theta_rad)]
        ])

    # Correction to apply
    # Half size of ETROC + half gap between them
    correction_x = ETROC_SIZE[0] / 2 + ETROC_GAP / 2
    correction_y = ETROC_SIZE[1] / 2 + ETROC_GAP / 2
    
    # Different position require the correction in different directions
    local_positions = {
            "A" : np.array([-correction_x, +correction_y]),
            "B" : np.array([-correction_x, -correction_y]),
            "C" : np.array([+correction_x, +correction_y]),
            "D" : np.array([-correction_x, +correction_y])
            }

    for letter, local_position in local_positions.items():
        # Transform PCB coordinates -> robot coordinates
        position = pcb_center + rotation @ local_position
        # Apply global correction, if defined in robot coordinates
        position += np.array(CORRECTION)
        place_pos[f"PCB_{module}{letter}"] = [
            position[0],
            position[1],
            theta_deg
        ]

    return place_pos

def TakePicFiducialMarks_PCB(modules_to_perform_assembly, etlcontroller, fiducial):
    """
    Acquire fiducial mark images for PCBs and compute their center positions 
    in robot coordinates.
    IMPORTANT: PICS MUST BE TAKEN IN A, B, C, D ORDER

    Parameters
    ----------
    modules_to_perform_assembly : list[int]
        List of module IDs to process.

    etlcontroller : object

    fiducial: str
        Name of the file with the fiducial positions

    Returns
    -------
    center_pos : dict
        Dictionary containing computed center positions in robot coordinates.
            center_pos["PCB_{module}"] = [x, y, rotation]
            center_pos["PCB_{module}{ETROC}"] = [x, y, rotation]
    """
    with open(fiducial) as f:
        positions = json.load(f)

    # Folder to store images
    folder_name = f"{PATH}/FiducialPCB"
    os.makedirs(folder_name, exist_ok=True)

    place_pos = {}
    # Take pic PCBs
    for i_module in modules_to_perform_assembly:
        corners = []
        valid = True
        for i_corner in range(4):
            pos = positions[str(i_module)][f"PCB_{i_module}"][i_corner]
            print(i_corner, pos)
            corner, i_valid = _locate_fiducial(etlcontroller, pos, folder_name=folder_name, part_name=f"PCB_{i_module}", is_ETROC=False)
            valid = valid and i_valid
            corners.append(corner)
        # Store raw corners
        raw_corners = _load_corners_json(folder_name)
        _save_corners_json(folder_name, raw_corners, f"PCB_{i_module}", corners)

        if not valid:
            continue

        # Compute center position of the ETROC
        corners = np.asarray(corners)
        pos = ComputePlacement_PCB(np.asarray(corners), i_module)
        place_pos.update(pos)
    return place_pos

def _locate_fiducial(etlcontroller, pos, folder_name, part_name, is_ETROC):

    if is_ETROC:
        th = 55
        etlcontroller.camera.set_exposure(0.03)
    else:
        th = 150
        etlcontroller.camera.set_exposure(0.025)
    x = pos["x"]
    y = pos["y"]
    z = pos["z"]
    rz = pos["rz"]
    # Autofocus
    print(f"Photo position = {x}, {y}, {z}, {rz}")
    etlcontroller.safeMovement(x, y, SAFE_Z, rz)
    summary, focus_z, fraction = etlcontroller.fullAutoFocus(z, is_double=True)
    etlcontroller.safeMovement(x, y, focus_z, None)

    # Take pic
    position_xyzrz = etlcontroller.getPositionXYZ()
    position_j1j2j3j4_rad = etlcontroller.getPositionJ1J2J3_rad()
    position_j1j2j3j4_deg = etlcontroller.getPositionJ1J2J3_deg()
    x_r, y_r, z_r, rz_r = position_xyzrz
    j1_r, j2_r, j3_r, j4_r = position_j1j2j3j4_deg
    image_name = f"{folder_name}/{part_name}X_{x_r:.3f}Y_{y_r:.3f}Z_{z_r:.3f}RZ_{rz_r:.3f}J1_{j1_r:.3f}J2_{j2_r:.3f}J3_{j3_r:.3f}J4_{j4_r:.3f}.png"
    etlcontroller.camera.changeFileName(image_name)
    etlcontroller.camera.takePic()
    # Procces pic and extract center
    p = ProcessFiducialPoint.ProcessFiducialPoint(image_name, is_ETROC=is_ETROC)
    x_pic, y_pic, valid = p.fit(th)
    if not valid:
        print("Fit not valid, wrong assignment of fiducial mark")
        return [None, None], False
    # Change from pixels to Robot Coordinates
    # XXX - I need to update robot simulation position
    etlcontroller.robot.JMoveRobotTo(position_j1j2j3j4_rad)
    x_reco_robot, y_reco_robot, z_reco_robot = etlcontroller.robot.cameraProjectionToPoint3D([x_pic, y_pic])
    print(f"Reconstructed position = {x_reco_robot}, {y_reco_robot}")

    return [x_reco_robot, y_reco_robot], True


def save_assembly_positions(assembly_parts_position, path):
    """
    Write the computed assembly positions to an intermediate JSON file, so the
    measurement phase (fiducial imaging) can be separated from the physical
    assembly phase and re-used without repeating the camera work.
    """
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        json.dump(assembly_parts_position, f, indent=4)
    print(f"Assembly positions written to {path}")



if __name__ == "__main__":
    
    parser = OptionParser(usage="%prog --help")
    parser.add_option("-i", "--ip", dest="ip", type="string", default="192.168.0.189", help="IP of the camera server.")
    parser.add_option("-p", "--port", dest="port", type=int, default=8080, help="Port of the camera server.")
    parser.add_option("-d", "--device", dest="device", type="string", default="/dev/ttyUSB0", help="Robot device name.")
    parser.add_option("-b", "--bauds", dest="bauds", type=int, default=115200, help="Robot bauds.")
    parser.add_option("-c", "--calibration", dest="calibration", type=str, default="ExperimentalSetup/Calibrations/calibrations.txt", help="Robot calibration file.")
    parser.add_option("-f", "--fiducial", dest="fiducial", type=str, default="runWorkflows/FiducialMarkPos.json", help="Fiducial mark positions file.")
    parser.add_option("--retake", dest="retake", type=str, default=None, help="Retakes photos instead of running whole workflow. Syntax is: 'ETROC:<hybrid>:<letter>:<corner>' or 'PCB:<module>:<corner>'. To use various at the same time separate them with comas.")
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
    # Initialize Camera
    robotCamera = RobotCamera(options.ip, options.port, 'picture.png', robot3D)
    
    # Initialize Robot
    etlcontroller = ETLController(options.device, options.bauds, robotCamera, robot3D, False)
    etlcontroller.camera.set_exposure(0.025)
    ################ END - Initialize Connections

    try:
        ################ Retake
        if options.retake:
            results = run_retakes(options.retake, etlcontroller, options.fiducial)
            print(f"Recomputed results: {results}")
        ################ END - Retake

        ################ Position Assembly Parts
        else:
            # Initialize position of assembly parts
            assembly_parts_position = {}

            # modules_to_perform_assembly = [1, 2, 3, 4]
            modules_to_perform_assembly = [1]
            # Take pictures of the fiducial marks in the ETROCs, compute and store centers
            etroc_pos = TakePicFiducialMarks_ETROC(modules_to_perform_assembly, etlcontroller, options.fiducial)
            assembly_parts_position.update(etroc_pos)
            # Take pictures of the fiducial marks in the PCB, compute each PCB placement
            pcb_pos = TakePicFiducialMarks_PCB(modules_to_perform_assembly, etlcontroller, options.fiducial)
            assembly_parts_position.update(pcb_pos)

            save_assembly_positions(assembly_parts_position, f"{PATH}/assembly_positions.json")
         ################ END - Position Assembly Parts
    except Exception as e:
        print(e)

    finally:
        ################ END -Assembly
        # Close connection
        etlcontroller.exit()
