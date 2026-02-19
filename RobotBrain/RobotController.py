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
    def __init__(self, device, bauds, robot3D):

        #Technical stuff
        self.HEADER = '\033[95m'
        self.OKBLUE = '\033[94m'
        self.OKGREEN = '\033[92m'
        self.FAIL = '\033[91m'
        self.ENDC = '\033[0m'
        self.msg_length = 512
        
        #Information for the client
        self.device = device
        self.bauds = bauds

        #Robot3D model
        self.robot3D = robot3D

        #Show off
        self.showBanner()

        #Create connection
        self.serial = serial.Serial(self.device, self.bauds, timeout=1)
        self.serial.open()

        self.printLog('Connection established')

        # Initialize robot control variables
        self.position_xyz = None
        self.position_j1j2j3 = None
        self.valves = None
        self.em = None

        #Do the handshake
        if not self.handshake():
            self.exit()
        
    ##############################################################################
    def stop(self):
        self.sendMessage('STOP')
        self.exit()

    ##############################################################################
    def handshake(self):
        
        self.printLog('Starting handshake')
        self.sendMessage('HI SERVER')
        
        data = self.getMessage()
        self.decodeMessage(data)
        # if data == 'HI CLIENT':
        #     self.printLog('Server says ' + data)
        #     self.sendMessage('HANDSHAKE CONFIRMED')
        #     return True
        # else:
        #     self.printError('Server Handshake response is not valid')
        #     self.exit()
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
    def printCom(self, text):

        print(self.OKBLUE + text + self.ENDC)
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
            msg = self.serial.rad(self.msg_length)
            text = text + msg.decode()
            counter = counter + len(msg)
            if counter == slf.msg_length:
                break
        # Message is of the form: "@@@@@POS:....ANGLES:.....VALVES:....EM:...."
        message = text[text.find('@@@@@'):text.find('XXXXX')]
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
        pattern = r'POS:(.*?)ANGLES:(.*?)VALVES:(.*?)EM:(.*)'
        match = re.search(pattern, msg)

        if not match:
            self.printError(f"Recived message of the robot {msg} does not have expected syntax")
            self.exit()

        pos_str, angles_str, valves_str, em_str = match.groups()
        pos = extract_numbers(pos_str)
        angles = extract_numbers(angles_str)
        # XXX - Check how the valve and EM status are sent, with or without sign?
        valves = extract_numbers(valves_str)
        em = extract_numbers(em_str)
        self.position_xyz = pos
        self.position_j1j2j3 = angles
        self.valves = valves
        self.em = em
        return True
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
        self.serial.write(msg.encode())
        return True
    ##############################################################################

  
    ##############################################################################
    def goTo(self, x, y, z, v):

        xs = str(x)
        ys = str(y)
        zs = str(z)
        vs = str(v)
        if x >= 0:
            xs = '+' + xs
        if y >= 0:
            ys = '+' + ys
        if z >= 0:
            zs = '+' + zs
        if v >= 0:
            vs = '+' + vs

        cadena = f'GOTO:{xs}{ys}{zs}{vs})'
        
        self.sendMessage(cadena)
        data = self.getMessage()
        self.decodeMessage(data)

        # Check the robot is in the desire position
        # XXX - Do I need to add some tolerance?
        if self.position_xyz == [x, y, z]:
            return True
        else:
            self.printError(f'Robot position ({self.position}) does not match the required position ({[x, y, z]})')
            self.exit()
            return False
    ##############################################################################
  
    ##############################################################################
    def askPosition(self):

        self.sendMessage('?')
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

