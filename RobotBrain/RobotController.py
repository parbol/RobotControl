# ____   ___   ____    ___   ______         __   ___   ____   ______  ____   ___   _      _        ___  ____  
#|    \ /   \ |    \  /   \ |      |       /  ] /   \ |    \ |      ||    \ /   \ | |    | |      /  _]|    \ 
#|  D  )     ||  o  )|     ||      |      /  / |     ||  _  ||      ||  D  )     || |    | |     /  [_ |  D  )
#|    /|  O  ||     ||  O  ||_|  |_|     /  /  |  O  ||  |  ||_|  |_||    /|  O  || |___ | |___ |    _]|    / 
#|    \|     ||  O  ||     |  |  |      /   \_ |     ||  |  |  |  |  |    \|     ||     ||     ||   [_ |    \ 
#|  .  \     ||     ||     |  |  |      \     ||     ||  |  |  |  |  |  .  \     ||     ||     ||     ||  .  \
#|__|\_|\___/ |_____| \___/   |__|       \____| \___/ |__|__|  |__|  |__|\_|\___/ |_____||_____||_____||__|\_|
#

import serial
import time
import sys
import os
import math
import re

class RobotController:

    ##############################################################################
    def __init__(self, device, bauds, debug = False):

        #Technical stuff
        self.HEADER = '\033[95m'
        self.OKBLUE = '\033[94m'
        self.OKGREEN = '\033[92m'
        self.FAIL = '\033[91m'
        self.ENDC = '\033[0m'
        self.WARNING = '\033[93m'
        self.msg_length = 128
        self.debug = debug
        
        #Information for the client
        self.device = device
        self.bauds = bauds

        #Show off
        self.showBanner()

        #Create connection
        self.serial = serial.Serial(self.device, self.bauds, timeout=1)

        self.printLog('Connection established')

        # Initialize robot control variables
        self.position_xyz = None
        self.position_j1j2j3 = None
        self.valves = None
        self.em = None

        # Set robot velocity as a percentage of the setted value in the GUI
        self.velocity = 100
        self.acceleration = 30
        self.deceleration = 30
        # Do the handshake
        if not self.handshake():
            print("Closing")
            self.exit()
    ##############################################################################

    ##############################################################################
    def handshake(self):
        
        self.printLog('Starting handshake')
        
        data = self.getMessage()
        self.printDebug(data)
        if not self.decodeMessage(data):
            return False
        self.printDebug(f"position = {self.position_xyz}")
        if self.position_xyz is not None and self.position_j1j2j3 is not None and \
            self.valves is not None and self.em is not None:
            return True
        else:
            return False
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
    def exit(self):
        self.printLog('Closing connection')
        self.serial.close()
        sys.exit()
    ##############################################################################

    ##############################################################################
    def showBanner(self):

        print( self.HEADER)
        print(' ____   ___   ____    ___   ______         __   ___   ____   ______  ____   ___   _      _        ___  ____ ') 
        print('|    \\ /   \ |    \\  /   \\ |      |       /  ] /   \\ |    \\ |      ||    \\ /   \\ | |    | |      /  _]|    \\') 
        print('|  D  )     ||  o  )|     ||      |      /  / |     ||  _  ||      ||  D  )     || |    | |     /  [_ |  D  )')
        print('|    /|  O  ||     ||  O  ||_|  |_|     /  /  |  O  ||  |  ||_|  |_||    /|  O  || |___ | |___ |    _]|    /')
        print('|    \\|     ||  O  ||     |  |  |      /   \\_ |     ||  |  |  |  |  |    \\|     ||     ||     ||   [_ |    \\') 
        print('|  .  \\     ||     ||     |  |  |      \     ||     ||  |  |  |  |  |  .  \\     ||     ||     ||     ||  .  \\')
        print('|__|\\_|\\___/ |_____| \\___/   |__|       \\____| \\___/ |__|__|  |__|  |__|\\_|\\___/ |_____||_____||_____||__|\\_|')
        print( self.ENDC)
        print( '\n\n')
    ##############################################################################

    ##############################################################################
    def getMessage(self):

        counter = 0
        text = ''
        while True:
            msg = self.serial.read(self.msg_length)
            text = text + msg.decode()
            counter = counter + len(msg)
            if counter == self.msg_length:
                break
        # Message is of the form: "@@@@@POS:....ANGLES:.....VALVES:....EM:...."
        message = text[text.find('@@@@@')+5:text.find('XXXXX')]
        self.printDebug(message)
        # Error message start with [ERROR]
        # Read it and log it differently
        if message.startswith("[ERROR]"):
            self.decodeErrorMessage(message)
            return False
        else:
            return message
    #############################################################################

    #############################################################################
    def decodeMessage(self, msg):
        """
        Decodes messages received from the robot
        They must have the form: "POS:....ANGLES:.....VALVES:10001..EM:1"
        where ... are signed numbers +2.4-32+56
        VALVES return a binary number with 1 meanning open and 0 closed
        EM return 1 bit with 1 meanning on and 0 off
        """
        self.printDebug(f"Received message: {msg}")
        pattern = r'POS:(.*?)ANGLE:(.*?)VALVES:(.*?)EM:(.*)'
        match = re.search(pattern, msg)

        if not match:
            self.printError(f"Received message of the robot *{msg}* does not have expected syntax")
            return False

        pos_str, angles_str, valves_str, em_str = match.groups()
        pos = self.extract_numbers(pos_str)
        angles = self.extract_numbers(angles_str)
        self.valves = valves_str
        self.em = em_str[0]
        self.position_xyz = pos
        self.position_j1j2j3 = angles
        return True
    #############################################################################
    
    #############################################################################
    def decodeErrorMessage(self, message):
        # TODO - Try to recover certain errors?
        self.printError(message)
        self.exit()
    #############################################################################

    #############################################################################
    def extract_numbers(self, s):
        return [float(x) for x in re.findall(r'[+-]?\d+(?:\.\d+)?', s)]
    #############################################################################

    ##############################################################################
    def sendMessage(self, msg):

        if len(msg) >= self.msg_length-10:
            return False 
        # Message structure: "@@@@@COMMAND:RelatedInfo_______...XXXXX
        msg = 5*'@' + msg
        for i in range(len(msg), self.msg_length-5):
            msg += '_'
        msg += 5*'X'
        self.printDebug(msg)
        self.serial.write(msg.encode())
        return True
    ##############################################################################
  
    ##############################################################################
    def getVelocity(self):
        return self.velocity

    def changeVelocity(self, v):
        if v >= 0 and v<=100:
            self.velocity = v
            return True
        else:
            self.printError(f"Velocity must be between 0 and 100, it is {v}")
            return False
    ##############################################################################

    ##############################################################################
    def getAcceleration(self):
        return self.acceleration

    def changeAcceleration(self, a):
        if a >= 0 and a<=100:
            self.acceleration = a
            return True
        else:
            self.printError(f"Aceleration must be between 0 and 100, it is {a}")
            return False
    ##############################################################################

    ##############################################################################
    def getDeceleration(self):
        return self.deceleration
    def changeDeceleration(self, a):
        if a >= 0 and a<=100:
            self.deceleration = a
            return True
        else:
            self.printError(f"Deceleration must be between 0 and 100, it is {a}")
            return False
    ##############################################################################

    ##############################################################################
    # Robot functions                                                           ##
    ##############################################################################

    ##############################################################################
    def goTo(self, x, y, z, rz):

        xs = str(x)
        ys = str(y)
        zs = str(z)
        rzs = str(rz)
        if x >= 0:
            xs = '+' + xs
        if y >= 0:
            ys = '+' + ys
        if z >= 0:
            zs = '+' + zs
        if rz >= 0:
            rzs = '+' + rzs
        if self.velocity >= 0:
            vs = '+' + str(self.velocity)
        if self.acceleration >= 0:
            acs = '+' + str(self.acceleration)
        if self.deceleration >= 0:
            dcs = '+' + str(self.deceleration)
        

        cadena = f'MOVE-TO:{xs}{ys}{zs}{rzs}{vs}{acs}{dcs}'
        
        self.sendMessage(cadena)
        data = self.getMessage()
        if not self.decodeMessage(data):
            self.printError(f'There was a problem decoding the message from the Robot')
            return False

        # Check the robot is in the desire position
        if (self.position_xyz[0] - x)**2 + (self.position_xyz[1] - y)**2 + (self.position_xyz[2] - z)**2 < 0.01**2: 
            return True
        else:
            print(f"Error position is not matching pos = {self.position_xyz}")
            self.askStatus()
            if (self.position_xyz[0] - x)**2 + (self.position_xyz[1] - y)**2 + (self.position_xyz[2] - z)**2 < 0.01**2: 
                return True
            else:
                self.printError(f'Robot position ({self.position_xyz}) does not match the required position ({[x, y, z]})')
                self.exit()
                return False
    ##############################################################################

    ##############################################################################
    def moveJ(self, j1, j2, j3, j4):

        j1s = str(j1)
        j2s = str(j2)
        j3s = str(j3)
        j4s = str(j4)
        if j1 >= 0:
            j1s = '+' + j1s
        if j2 >= 0:
            j2s = '+' + j2s
        if j3 >= 0:
            j3s = '+' + j3s
        if j4 >= 0:
            j4s = '+' + j4s
        if self.velocity >= 0:
            vs = '+' + str(self.velocity)

        cadena = f'MOVE-J:{j1s}{j2s}{j3s}{j4s}{vs}'
        
        self.sendMessage(cadena)
        data = self.getMessage()
        if not self.decodeMessage(data):
            self.printError(f'There was a problem decoding the message from the Robot')
            return False

        # Check the robot is in the desire position
        if (self.position_j1j2j3[0] - j1)**2 + (self.position_j1j2j3[1] - j2)**2 + (self.position_j1j2j3[2] - j3)**2 < 0.01**2: 
            return True
        else:
            print(f"Error position is not matching pos = {self.position_j1j2j3}")
            time.sleep(1)
            self.askStatus()
            if (self.position_j1j2j3[0] - j1)**2 + (self.position_j1j2j3[1] - j2)**2 + (self.position_j1j2j3[2] - j3)**2 < 0.01**2: 
                return True
            else:
                self.printError(f'Robot position ({self.position_j1j2j3}) does not match the required position ({[j1, j2, j3]})')
                return False
    ##############################################################################

    ##############################################################################
    def setEM(self, status):
        """
        Set ElectroMagnet Status. 
        Parameters:
        ---------------------------
            status: int
                0 or 1. 0 meaning Off and 1 meaning On
        """
        status_str = str(status)
        if status_str not in ('0','1'):
            self.printError(f'Not valid status of the electromagnet, it can be 0 or 1 and required status is {status_str}')
            return False
        
        cadena = f'SET-EM:{status_str}'
        self.sendMessage(cadena)
        data = self.getMessage()
        self.decodeMessage(data)
        # Check the EM is in the desire status
        if str(self.em) == str(status):
            return True
        else:
            self.printError(f'Electromagnet status ({self.em}) does not match the required status ({status})')
            self.exit()
            return False
    ##############################################################################

    ##############################################################################
    def setValves(self, status):
        """
        Set ElectroMagnet Status. 
        Parameters:
        ---------------------------
            status: str
                20 bits together, 1 per valve in the system. 0 or 1. 0 meaning Off and 1 meaning On
        """
        status_str = str(status)
        if len(status_str) !=32 or any(c not in '01' for c in status_str):
            self.printError(f'Not valid status of the valves, it can be 0 or 1 and required status is {status_str}')
            return False
        
        cadena = f'SET-VALVES:{status_str}'
        self.sendMessage(cadena)
        data = self.getMessage()
        self.decodeMessage(data)
        # Check the EM is in the desire status
        if str(self.valves) == str(status_str):
            return True
        else:
            self.printError(f'Valves status ({self.valves}) does not match the required status ({status})')
            self.exit()
            return False
    ##############################################################################

    ##############################################################################
    def stop(self):
        self.sendMessage('STOP:')
        self.exit()
    ##############################################################################

    ##############################################################################
    def wait_user(self):
        """
        Waits until the user interacts with the tablet GUI of the robot
        """
        self.sendMessage('WAIT-USER')
        data = self.getMessage()
        self.decodeMessage(data)
        return True
    ##############################################################################

    ##############################################################################
    def wait_time(self, seconds: int):
        """
        Waits a certain time until the robot sends the STATUS message back. It keeps the robot-pc connection open"
        Parameters:
            seconds : int
                Seconds to wait
        """
        if isinstance(seconds, int):
            pass
        elif isinstance(seconds, float):
            seconds_int = int(seconds)
            self.printWarning(f"Wait time must be an integer, given a float ({seconds}), converted to int ({seconds_int}).")
            seconds = seconds_int
        elif isinstance(seconds, str):
            try:
                seconds = int(seconds)
                self.printWarning(f"Wait time must be an integer, given a str, converted to int ({seconds}).")

            except (ValueError, TypeError):
                self.printError(f'Wait time must be an integer. Given: {seconds}')
                self.exit()
                return False
        else:
            self.printError(f'Wait time must be numeric. Given {seconds}, {type(seconds)}')
            self.exit()
        if seconds < 0:
            self.printError(f'Wait time must be positive. Given: {seconds}')
            self.exit()
            return False

        message = f'WAIT-TIME:{seconds}'
        self.sendMessage(message)
        data = self.getMessage()
        self.decodeMessage(data)
        return True
    ##############################################################################

    ##############################################################################
    def askStatus(self):
        self.sendMessage('NOTHING')
        data = self.getMessage()
        self.decodeMessage(data)
        return True
    ##############################################################################

    ##############################################################################
    # Getters                                                                   ##
    ##############################################################################

    def getPositionXYZ(self):
        return self.position_xyz
    def getPositionJ1J2J3(self):
        return self.position_j1j2j3
    def getValveStatus(self):
        return self.valves
    def getEM(self):
        return self.em

    ##############################################################################

