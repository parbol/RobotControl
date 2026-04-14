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
from RobotBrain.RobotController import RobotController

class ETLController:

    ##############################################################################
    def __init__(self, device, bauds, camera, robot3D, debug = False):
    #TODO: Implementar si es modo ETL comprobar j2 si es <0 left-handed --> ETL ok. Si no mover a punto seguro (TODO: buscar el pto), luego mover angular j2 (TODO funcion angular llamada MOVE-J:j1+-...j2+-...j3+-...j4+-...) rechekear y is_ETL = true

        self.HEADER = '\033[95m'
        self.OKBLUE = '\033[94m'
        self.OKGREEN = '\033[92m'
        self.FAIL = '\033[91m'
        self.ENDC = '\033[0m'
        self.WARNING = '\033[93m'
        self.msg_length = 128
        self.debug = debug
        
        # Information for the client
        self.robotcontroller = RobotController(device, bauds, camera, robot3D, debug)

        # Show off
        self.showBanner()
        time.sleep(1)

        # Actual position
        self.robotcontroller.askStatus()
        self.updateStatus()

        # Movement information
        self.safe_z = 180
        self.picker_tool = [-332.36, 173.79, 94,-161.17]
        # self.safe_pos_rotate_arm = [x, y, self.safe_z]
        
        # Initialise arm in ETL mode, ETL is left handed, IT is right handed
        self.checkArmPlacement()
        while not self._is_left_handed:
            self.rotateArm(left_handed=True)
            self.checkArmPlacement()
        self.checkArmPlacement()
        while self._is_left_handed:
            self.rotateArm(left_handed=False)
            self.checkArmPlacement()
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
        # TODO if i need to go to right handed i need another safe pos
        # Or use the diagona j1 -45 to avoid collisions with the robot
        # Check if current orientation is the final one
        if self.checkArmPlacement() != left_handed:
            final_j2 = -90 if left_handed else 90
            safe_j2 = 90 if left_handed else -90
            self.updateStatus()
            print(self.position_xyzrz)
            # Move to safe pos
            self.safeMovement(self.position_xyzrz[0], self.position_xyzrz[1], self.safe_z, self.position_xyzrz[3])
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
        self.position_xyzrz = self.robotcontroller.getPositionXYZ()
        self.position_j1j2j3j4 = self.robotcontroller.getPositionJ1J2J3()
        self.valves = self.robotcontroller.getValveStatus()
        self.em = self.robotcontroller.getEM()

    ##############################################################################

    ##############################################################################
    def safeMovement(self, x, y, z, rz):
        # Go up to safe z
        self.updateStatus()
        self.robotcontroller.goTo(self.position_xyzrz[0], self.position_xyzrz[1], self.safe_z, self.position_xyzrz[3])
        self.updateStatus()
        # Move to desired pos and safe z
        self.robotcontroller.goTo(x, y, self.safe_z, rz)
        self.updateStatus()
        # Move to desired pos 
        self.robotcontroller.goTo(x, y, z, rz)
        self.updateStatus()
        return True
    ##############################################################################

    # ##############################################################################
    def grabPickerTool(self):
        self.safeMovement(self.picker_tool[0], self.picker_tool[1], self.picker_tool[2], self.picker_tool[3])
        self.robotcontroller.setEM(1)
        self.updateStatus()
        self.robotcontroller.goTo(self.position_xyzrz[0], self.position_xyzrz[1], self.safe_z, self.position_xyzrz[3])
        return True
    # ##############################################################################

    # ##############################################################################
    # def releasePickerTool(self):

    # ##############################################################################

    # ##############################################################################
    # def grabAssemblyPart(self, x, y, z, rz):

    # ##############################################################################

    # ##############################################################################
    # def releaseAssemblyPart(self, x, y, z, rz):

    # ##############################################################################

    # ##############################################################################
    # def moveToPhoto(self, x, y, z, rz):

    # ##############################################################################
    # 
    # ##############################################################################
    # def moveBetweenPhotos(self, x, y, z, rz):

    # ##############################################################################

    # ##############################################################################
    # def wait_user(self):
    # # Needed?
    # ##############################################################################

    # ##############################################################################
    # def wait_time(self, seconds: int):
    # Needed?
    ##############################################################################

    ##############################################################################
    # Getters                                                                   ##
    ##############################################################################

    def getPositionXYZ(self):
        robotcontroller.askStatus()
        return self.position_xyz
    def getPositionJ1J2J3(self):
        robotcontroller.askStatus()
        return self.position_j1j2j3
    def getValveStatus(self):
        robotcontroller.askStatus()
        return self.valves
    def getEM(self):
        robotcontroller.askStatus()
        return self.em

    ##############################################################################

    ##############################################################################
    def exit(self):
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
        print(' ____   ______   ____         __   ___   ____   ______  ____   ___   _      _        ___  ____')
        print('|    | |      | |    |       /  ] /   \ |    \ |      ||    \ /   \ | |    | |      /  _]|    \ ') 
        print('|  __| |_    _| |    |      /  / |     ||  _  ||      ||  D  )     || |    | |     /  [_ |  D  )')
        print('| |__    |  |   |    |     /  /  |  O  ||  |  ||_|  |_||    /|  O  || |___ | |___ |    _]|    /') 
        print('|  __|   |  |   |    |__  /   \_ |     ||  |  |  |  |  |    \|     ||     ||     ||   [_ |    \ ') 
        print('| |__    |  |   |       | \     ||     ||  |  |  |  |  |  .  \     ||     ||     ||     ||  .  \ ')
        print('|____|   |__|   |_______|  \____| \___/ |__|__|  |__|  |__|\_|\___/ |_____||_____||_____||__|\_|')
        print( self.ENDC)
        print( '\n\n')
    ##############################################################################
