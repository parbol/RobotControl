# ____   ______   ____         __   ___   ____   ______  ____   ___   _      _        ___  ____  
#|    | |      | |    |       /  ] /   \ |    \ |      ||    \ /   \ | |    | |      /  _]|    \ 
#|  __| |_    _| |    |      /  / |     ||  _  ||      ||  D  )     || |    | |     /  [_ |  D  )
#| |__    |  |   |    |     /  /  |  O  ||  |  ||_|  |_||    /|  O  || |___ | |___ |    _]|    / 
#|  __|   |  |   |    |__  /   \_ |     ||  |  |  |  |  |    \|     ||     ||     ||   [_ |    \ 
#| |__    |  |   |       | \     ||     ||  |  |  |  |  |  .  \     ||     ||     ||     ||  .  \
#|____|   |__|   |_______|  \____| \___/ |__|__|  |__|  |__|\_|\___/ |_____||_____||_____||__|\_|
#

import serial
import time
import sys
import os
import math
import re
import numpy as np
from RobotBrain.RobotController import RobotController

class ETLController:

    ##############################################################################
    def __init__(self, device, bauds, camera, robot3D, debug=False):
        """
        All angular coordinates are in deg

        """

        self.HEADER = '\033[95m'
        self.OKBLUE = '\033[94m'
        self.OKGREEN = '\033[92m'
        self.FAIL = '\033[91m'
        self.ENDC = '\033[0m'
        self.WARNING = '\033[93m'
        self.msg_length = 128
        self.debug = debug
        
        # Information for the client
        self.robotcontroller = RobotController(device, bauds, debug)

        # Camera
        self.camera = camera
        # Robot model
        self.robot = robot3D

        # Show off
        self.showBanner()
        time.sleep(1)

        # Actual position
        self.robotcontroller.askStatus()
        self.updateStatus()

        # Movement information
        self.safe_z = 180
        self.safe_rz = 60
        self.picker_tool = [-332.36, 173.79, 91.13,-161.17]
        self.safe_position = [-361.43, -421.93, self.safe_z, self.safe_rz]
        # Plate central position in angular coordinates
        # TODO - update j4
        self.plate_position_j1j2j3j4 = { 1: [-30, -70, self.safe_z, 107], 
                                         2: [-98, -78, self.safe_z, 107],
                                         3: [-116, -115, self.safe_z, 107],
                                         4: [-170, -110, self.safe_z, 80],
                                        }
        # Plate central position in cartesian coordinates, similar to previous but different rounding
        # TODO check when does Y change sign
        self.plate_position_xyzrz = {1: [292, -417, self.safe_z, 107], 
                                     2: [-292, -390, self.safe_z, 107],
                                     3: [-319, -155, self.safe_z, 107],
                                     4: [-332, 174, self.safe_z, -161]
                                     }
       
        # Limits to avoid collision
        # Define one region for picker tool and assembly, another region for Tamale plate
        self.x_limit = -230

        # Valves mapping -1 for correct index
        base_map = {
            "A": 14,
            "B": 15,
            "C": 16,
            "D": 17,
        }

        self.valve_map = {}
        for i_module in range(1, 5):
            offset = 4 * (i_module - 1)

            for etroc, base_valve in base_map.items():
                self.valve_map[f"ETROC_{i_module}{etroc}"] = [base_valve + offset]

        self.valve_map["PCB"] = [12]
        self.valve_map["COVER"] = [13]
        self.valve_map["TOOL"] = [30, 31]

        # Initialise arm in ETL mode, ETL is left handed, IT is right handed
        self.checkArmPlacement()
        while not self._is_left_handed:
            self.rotateArm(left_handed=True)
            self.checkArmPlacement()

    ##############################################################################
    ##  ETL functions                                                           ##
    ##############################################################################

    ##############################################################################
    def checkArmPlacement(self):
        self.updateStatus()
        if self.position_j1j2j3j4[1]<= 0:
            self._is_left_handed = True
            return True
        else:
            self._is_left_handed = False
            return False
    ##############################################################################

    ##############################################################################
    def rotateArm(self, left_handed = True):
        # Use the diagona j1 -45 to avoid collisions with the robot
        # Use a safe j2 or +-90 to avoid colisions while going to j1 = -45
        # Check if current orientation is the final one
        if self.checkArmPlacement() != left_handed:
            final_j2 = -90 if left_handed else 90
            safe_j2 = 90 if left_handed else -90
            self.updateStatus()
            # Move to safe z 
            self.changeZ(self.safe_z)
            self.updateStatus()

            # Rotate safe j2
            self.robotcontroller.moveJ(self.position_j1j2j3j4[0], safe_j2, self.position_j1j2j3j4[2], self.position_j1j2j3j4[3]) 
            self.updateStatus()
            # Rotate j1
            self.robotcontroller.moveJ(-45, self.position_j1j2j3j4[1], self.position_j1j2j3j4[2], self.position_j1j2j3j4[3]) 
            self.updateStatus()
            # Rotate j2
            self.robotcontroller.moveJ(self.position_j1j2j3j4[0], final_j2, self.position_j1j2j3j4[2], self.position_j1j2j3j4[3]) 
            self.updateStatus()

            self.robotcontroller.goTo(self.position_xyzrz[0], self.position_xyzrz[1], self.position_xyzrz[2], self.position_xyzrz[3])
            if self.checkArmPlacement() == left_handed:
                return True
            else:
                self.printError("Could not rotate the arm to the desire configuration")
                self.exit()
                return False
            
        else:
            return True
    ##############################################################################

    ##############################################################################
    def updateStatus(self):
        self.robotcontroller.askStatus()
        self.position_xyzrz = self.robotcontroller.getPositionXYZ()
        self.position_j1j2j3j4 = self.robotcontroller.getPositionJ1J2J3()
        self.valves = self.robotcontroller.getValveStatus()
        self.em = self.robotcontroller.getEM()

    ##############################################################################

    ##############################################################################
    def safeMovement(self, x, y, z, rz):
        """
        If rz = None it does not change
        """
        self.updateStatus()
        if rz == None:
            rz = self.position_xyzrz[3]
        self.printLog(f"Moving to {[x, y, z, rz]}")
        # Go up to safe z
        self.updateStatus()
        self.changeZ(self.safe_z)
        self.updateStatus()
        # XXX - Check colision with the robot as a minimum radio or something similar?
        # Check if changing plate
        self.printDebug("Compute current plate")
        current_plate = self.distanceToPlate(self.position_xyzrz)
        self.printDebug("Compute final plate")
        target_plate = self.distanceToPlate([x, y, z, rz])

        if current_plate != target_plate:
            self.changePlate(target_plate)
        self.updateStatus()

        # Check if changing region
        if (self.position_xyzrz[0] - self.x_limit) * (x - self.x_limit) <= 0:
            self.printLog("Crossing x limit = {self.x_limit}, following safety path")

            self.rotateRZ(self.safe_rz)
            self.updateStatus()
            
            self.robotcontroller.goTo(self.safe_position[0], self.safe_position[1], self.safe_position[2], self.safe_position[3])
            self.updateStatus()
            
            self.rotateRZ(self.safe_rz)
        self.updateStatus()

        self.printLog(f"Moving to final position, (X,Y) = ({x}, {y})")
        self.robotcontroller.goTo(x, y, self.safe_z, self.position_xyzrz[3])
        self.updateStatus()

        # Rotate head
        self.printLog(f"Moving to final position, RZ = {rz}")
        self.rotateRZ(rz)
        self.updateStatus()

        # Move to desired pos 
        self.printLog(f"Moving to final position, Z = {z}")
        self.changeZ(z)
        self.updateStatus()
        return True

    ##############################################################################

    ##############################################################################
    def changePlate(self, final_plate):
        self.updateStatus()
        # Compute closest plate position
        closest_plate = self.distanceToPlate(self.position_xyzrz)
        self.printLog(f"Moving from plate {closest_plate} to {final_plate}")
        
        # Rotate rz to this plate pos
        self.printLog(f"Preparing RZ to match the plate safe position")
        self.rotateRZ(self.plate_position_xyzrz[closest_plate][3])
        self.updateStatus()
        
        # Move angular to safe position of this plate
        self.printLog(f"Moving angular to plate safe position")
        self.rotateRZ(self.plate_position_xyzrz[closest_plate][3])
        self.robotcontroller.moveJ(
                self.plate_position_j1j2j3j4[closest_plate][0], 
                self.plate_position_j1j2j3j4[closest_plate][1], 
                self.plate_position_j1j2j3j4[closest_plate][2], 
                self.plate_position_j1j2j3j4[closest_plate][3]
                )
        self.updateStatus()
        
        # Move to final plate without changing rZ
        self.printLog(f"Moving angular to final plate safe position")
        self.robotcontroller.moveJ(
                self.plate_position_j1j2j3j4[final_plate][0], 
                self.plate_position_j1j2j3j4[final_plate][1], 
                self.plate_position_j1j2j3j4[final_plate][2], 
                self.plate_position_j1j2j3j4[closest_plate][3]
                )
        self.updateStatus()
        
        # Change rZ 
        self.printLog(f"RZ is safe final plate position")
        self.rotateRZ(self.plate_position_xyzrz[final_plate][3])
        self.updateStatus()
        
        return True
        
    ##############################################################################

    ##############################################################################
    def distanceToPlate(self, position):
        """
        Computes the closest plate to a given position and returns the closest plane
        """
        distance2 = {}
        self.printDebug(f"Position = {position}")
        for key, item in self.plate_position_xyzrz.items():
            self.printDebug(key)
            self.printDebug(f"{self.plate_position_xyzrz[key][0]}, {self.plate_position_xyzrz[key][1]}")
            distance2[key] = (position[0] - self.plate_position_xyzrz[key][0])**2 + (position[1] - self.plate_position_xyzrz[key][1])**2
        self.printDebug(distance2)
        closest = min(distance2, key=distance2.get)
        self.printDebug(closest)
        return closest
        
    ##############################################################################

    ##############################################################################
    def changeZ(self, z):
        self.updateStatus()
        self.printLog(f"Moving to z = {z}")
        # XXX - Define a range of safe z?
        self.robotcontroller.goTo(self.position_xyzrz[0], self.position_xyzrz[1], z, self.position_xyzrz[3])
        self.updateStatus()
        return True
        
    ##############################################################################

    ##############################################################################
    def rotateRZ(self, rz):
        # XXX - TO BE TESTED
        """
        rZ in the robot is defined as:
                    +-180
                +90         -90
                        0
        """
        self.updateStatus()
        self.printLog(f"Moving rZ from {self.position_xyzrz[3]} to {rz}")
        if self.position_xyzrz[3] < 0:
            # Move to +180 or 0, the closest one then move to the final position
            safe_rz = 0 if abs(self.position_xyzrz[3] - 0) <= abs(self.position_xyzrz[3]+180) else 180
            self.printLog(f"Initial rZ is negative --> going to {safe_rz}")
            self.robotcontroller.goTo(self.position_xyzrz[0], self.position_xyzrz[1], self.position_xyzrz[2], safe_rz)
            self.updateStatus()
        if rz < 0:
            # Move to 0 or +180, the closest one, then to the final one
            safe_rz = 0 if abs(rz - 0) <= abs(rz+180) else 180
            self.printLog(f"Final rZ is negative --> going to {safe_rz}")
            self.robotcontroller.goTo(self.position_xyzrz[0], self.position_xyzrz[1], self.position_xyzrz[2], safe_rz)
            self.updateStatus()

        # Final movement
        self.robotcontroller.goTo(self.position_xyzrz[0], self.position_xyzrz[1], self.position_xyzrz[2], rz)
        self.updateStatus()
        return True
        
    ##############################################################################

    ##############################################################################
    def stepRZ(self, step_rz):
        if abs(step_rz) > 20:
            self.printError("The step rotation is too big check piece placements again IDIOT")
        self.updateStatus()
        final_rz = self.position_xyzrz[3] + step_rz
        self.robotcontroller.goTo(self.position_xyzrz[0], self.position_xyzrz[1], self.position_xyzrz[2], final_rz)
        self.updateStatus()
        return True

    ##############################################################################

    ##############################################################################
    def grabPickerTool(self):
        self.safeMovement(self.picker_tool[0], self.picker_tool[1], self.safe_z, self.picker_tool[3])
        self.changeZ(self.picker_tool[2]+10)
        v = self.getVelocity()
        self.setVelocity(10)
        self.changeZ(self.picker_tool[2])
        self.robotcontroller.setEM(1)
        self.setVelocity(v)
        time.sleep(1)
        self.updateStatus()
        self.changeZ(self.safe_z)
        return True

    ##############################################################################

    ##############################################################################
    def releasePickerTool(self):
        self.safeMovement(self.picker_tool[0], self.picker_tool[1], self.safe_z, self.picker_tool[3])
        self.changeZ(self.picker_tool[2]+10)
        v = self.getVelocity()
        self.setVelocity(10)
        self.changeZ(self.picker_tool[2])
        self.robotcontroller.setEM(0)
        self.setVelocity(v)
        time.sleep(1)
        self.updateStatus()
        self.changeZ(self.safe_z)
        return True
    ##############################################################################


    ##############################################################################
    def grabAssemblyPart(self, x, y, z, part_rotation_rz, part_name):
        self.updateStatus()
        if part_name.startswith("PCB"):
            safe_pos = self.plate_position_xyzrz[1]
        elif part_name.startswith("ETROC"):
            safe_pos = self.plate_position_xyzrz[2]
        elif part_name.startswith("COVER"):
            safe_pos = self.plate_position_xyzrz[3]
        else:
            self.printWarning("I do not know which plate I am loooking for")
            safe_pos = self.position_xyzrz
        # Move X-Y to part position and rz safe pos
        self.safeMovement(x, y, safe_pos[2], safe_pos[3])
        self.updateStatus()
        # Step in RZ to correct rotation
        self.stepRZ(part_rotation_rz)
        self.updateStatus()
        
        is_picked = False
        while not is_picked:
            self.changeZ(z)
            # Open Tool valves
            self.printLog("Openning tool valves")
            valves = self.nameToValves("TOOL", True)
            self.robotcontroller.setValves(valves)
            time.sleep(1)
            self.printLog(f"Clossing {part_name} valves")
            valves = self.nameToValves(part_name, False)
            self.robotcontroller.setValves(valves)
            time.sleep(2)

            self.updateStatus()
            self.changeZ(self.safe_z)

            result = input("Do you need to repeat the picking up process? (y/n)")
            if result.upper() == "N":
                is_picked = True
        return True

    ##############################################################################

    ##############################################################################
    def releaseAssemblyPart(self, x, y, z, part_rotation_rz, part_name):
        self.updateStatus()
        if part_name.startswith("PCB"):
            safe_pos = self.plate_position_xyzrz[1]
        elif part_name.startswith("ETROC"):
            safe_pos = self.plate_position_xyzrz[2]
        elif part_name.startswith("COVER"):
            safe_pos = self.plate_position_xyzrz[3]
        else:
            self.printWarning("I do not know which plate I am loooking for")
            safe_pos = self.position_xyzrz
        # Move X-Y to part position and rz safe pos
        self.safeMovement(x, y, safe_pos[2], safe_pos[3])
        self.updateStatus()
        # Step in RZ to correct rotation
        self.stepRZ(part_rotation_rz)
        self.updateStatus()
        # Go down
        self.changeZ(z)
        self.updateStatus()
        # Close Tool valves
        self.printLog("Closing tool valves")
        valves = self.nameToValves("TOOL", False)
        self.robotcontroller.setValves(valves)
        time.sleep(2)
        # Move up
        self.updateStatus()
        self.changeZ(self.safe_z)
        return True

    ##############################################################################

    ##############################################################################
    def nameToValves(self, name: str, to_open: bool):
        self.updateStatus()
        valves = list(self.valves)

        for valve in self.valve_map[name.upper()]:
            valves[valve] = "1" if to_open else "0"

        return "".join(valves)

    ##############################################################################
    
    ##############################################################################
    def fullAutoFocus(self, z_estimation, is_double=True):
        self.updateStatus()
        self.changeZ(z_estimation)
        
        # General focus 
        summary, focus_z, fraction = self._singleAutoFocus(z_range=1, z_speed=0.03, up_down=True)
        if is_double:
            # Change Z to focus one
            self.changeZ(focus_z)

            # Second focus from bottom to top
            summary, focus_z, fraction = self._singleAutoFocus(z_range=0.2, z_speed=0.005, up_down=False)
            return summary, focus_z, fraction
        else:
            return summary, focus_z, fraction
    ##############################################################################

    ##############################################################################
    def _singleAutoFocus(self, z_range, z_speed, up_down=True):
        """
        Perform a fast autofocus scan along the Z axis and estimate the best focus position.

        The autofocus procedure moves the robot from the upper bound of the scan range
        to the lower bound while the camera continuously acquires autofocus data.
        
        Parameters
        ----------
        z_range : float
            Total Z distance covered during the autofocus scan. The scan starts at ``z + z_range / 2`` and ends at
            ``z - z_range / 2``.
        z_speed : float
            Z-axis velocity used during the autofocus scan.
        up_down : bool, optional
            If ``True``, the autofocus is performed from top to bottom. 
            If `False``bottom to top. Default is ``True``.

        Returns
        -------
        summary : object
            Summary information returned by
            ``camera.stop_autofocusAcquisition()``.

        focus_z : float
            Estimated Z position corresponding to the best focus.
    
        fraction : float
            Relative focus position within the scan range, typically between 0 and 1.

        Notes
        -----
        - Assumes that the current XY and rotational positions are already correct.
        - The robot velocity is restored to its original value after the scan,
          even if an exception occurs during motion.
        """
        # XXX - Assuming XY and RZ positions are ok
        # move to position but z = position("z")+z_range/2 (start position of autofocus)
        self.updateStatus()
        z = self.position_xyzrz[2]
        if up_down:
            start_z = z + z_range / 2
            end_z   = z - z_range / 2
        else:
            start_z = z - z_range / 2
            end_z   = z + z_range / 2


        # init camera autofocus_acquisition

        # move to position but z = position("z")-z_range/2 and speed = z_speed
        stored_speed = self.getVelocity()
        self.setVelocity(z_speed)
        stored_acceleration = self.getAcceleration()
        self.setAcceleration(100)

        max_retries = 3
        for attemp in range(max_retries):
            self.changeZ(start_z)
            
            self.printLog("Starting autofocus")
            if not self.camera.start_autofocusAcquisition():
                raise RuntimeError("Could not start autofocus acquisition")
            
            summary = None
            try:
                self.changeZ(end_z)
            # stop autofocus_acquisition and get summary
            finally:
                summary = self.camera.stop_autofocusAcquisition()

            fraction = self.camera.estimate_focusFraction()

            if fraction is not None:
                break
            else:
                self.printWarning(f"Autofocus failed at attemp {attemp}")
            # for i in range(3):
            #     if self.camera.handshake():
            #         break
            # else: 
            #     self.printError("Loose connection to camera check cable")
        else:
            self.printError("Autofocus failed after 3 attemps")

        if up_down:
            focus_z = start_z - fraction * z_range
        else:
            focus_z = start_z + fraction * z_range
        self.printDebug(f"Autofocus fraction = {fraction}, focus_z = {focus_z}")
        # Go back to prev. speed and move to estimated focus
        self.setVelocity(stored_speed)
        self.setAcceleration(stored_acceleration)
        return summary, focus_z, fraction
    ##############################################################################

    # ##############################################################################
    # def wait_user(self):
    # Needed?
    # ##############################################################################

    # ##############################################################################
    # def wait_time(self, seconds: int):
    # Needed?
    ##############################################################################
    
    ##############################################################################
    # Setters                                                                   ##
    ##############################################################################

    def setVelocity(self, v):
        if v >= 0 and v<=100:
            self.robotcontroller.changeVelocity(v)
            return True
        else:
            self.printError(f"Velocity must be between 0 and 100, it is {v}")
            # XXX - Close connection?
            return False

    def setAcceleration(self, a):
        if a >= 0 and a<=100:
            self.robotcontroller.changeAcceleration(a)
            self.robotcontroller.changeDeceleration(a)
            return True
        else:
            self.printError(f"Acceleration must be between 0 and 100, it is {a}")
            # XXX - Close connection?
            return False
    ##############################################################################
    # Getters                                                                   ##
    ##############################################################################

    def getPositionXYZ(self):
        self.robotcontroller.askStatus()
        self.updateStatus()
        return self.position_xyzrz
    def getPositionJ1J2J3_deg(self):
        self.robotcontroller.askStatus()
        self.updateStatus()
        return self.position_j1j2j3j4
    def getPositionJ1J2J3_rad(self):
        self.robotcontroller.askStatus()
        self.updateStatus()
        j1 = np.radians(self.position_j1j2j3j4[0])
        j2 = np.radians(self.position_j1j2j3j4[1])
        j3 = self.position_j1j2j3j4[2] # This is z in mm
        j4 = np.radians(self.position_j1j2j3j4[3])
        return [j1, j2, j3, j4]
    def getValveStatus(self):
        self.robotcontroller.askStatus()
        self.updateStatus()
        return self.valves
    def getEM(self):
        self.robotcontroller.askStatus()
        self.updateStatus()
        return self.em
    def getVelocity(self):
        return self.robotcontroller.getVelocity()
    def getAcceleration(self):
        ac = self.robotcontroller.getAcceleration()
        dc = self.robotcontroller.getDeceleration()
        if ac == dc:
            return ac
        else:
            self.printError("Acceleration and deceleration have different values")
            return False

    ##############################################################################

    ##############################################################################
    def exit(self):
        if self.camera is not None:
            self.camera.stop()
        self.robotcontroller.stop()
    ##############################################################################

    ##############################################################################
    def printLog(self, text):

        print(self.OKGREEN + '[Log] ' + text + self.ENDC)
    ##############################################################################

    ##############################################################################
    def printError(self, text):

        print(self.FAIL + '[Error] ' + text + self.ENDC)
    ##############################################################################

    ##############################################################################
    def printWarning(self, text):

        print(self.WARNING + '[Warning] ' + text + self.ENDC)
    ##############################################################################

    ##############################################################################
    def printCom(self, text):

        print(self.OKBLUE + text + self.ENDC)
    ##############################################################################

    ##############################################################################
    def printDebug(self, text):
        if self.debug:
            print(f"[DEBUG]: {text}")
    ##############################################################################

    ##############################################################################
    def showBanner(self):

        print( self.HEADER)
        print(' ____   ______   ____         __   ___   ____   ______  ____   ___   _      _        ___  ____   ')
        print('|    | |      | |    |       /  ] /   \ |    \ |      ||    \ /   \ | |    | |      /  _]|    \  ')
        print('|  __| |_    _| |    |      /  / |     ||  _  ||      ||  D  )     || |    | |     /  [_ |  D  ) ')
        print('| |__    |  |   |    |     /  /  |  O  ||  |  ||_|  |_||    /|  O  || |___ | |___ |    _]|    /  ')
        print('|  __|   |  |   |    |__  /   \_ |     ||  |  |  |  |  |    \|     ||     ||     ||   [_ |    \  ')
        print('| |__    |  |   |       | \     ||     ||  |  |  |  |  |  .  \     ||     ||     ||     ||  .  \ ')
        print('|____|   |__|   |_______|  \____| \___/ |__|__|  |__|  |__|\_|\___/ |_____||_____||_____||__|\_| ')
        print( self.ENDC)
        print( '\n\n')
    ##############################################################################
