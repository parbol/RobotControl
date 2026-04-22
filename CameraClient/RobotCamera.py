import numpy as np
from ExperimentalSetup.Robot import Robot
import socket
import time
import sys
import os
import math

class RobotCamera:

    ##############################################################################
    def __init__(self, robot_IP, robot_PORT, filenameInput, robot3D):

        #Technical stuff
        self.HEADER = '\033[95m'
        self.OKBLUE = '\033[94m'
        self.OKGREEN = '\033[92m'
        self.FAIL = '\033[91m'
        self.ENDC = '\033[0m'
        
        #Information for the client
        self.robot_IP = robot_IP
        self.robot_PORT = robot_PORT
        self.fileName = filenameInput

        #3D model
        self.robot3D = robot3D

        #Show off
        self.showBanner()

        #Create connection
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.robot_IP, self.robot_PORT))
        self.printLog('Connection to: ' + str(robot_IP) + ' using port: ' + str(robot_PORT))

        #Do the handshake
        if not self.handshake():
            self.exit()
        

    ##############################################################################
    def changeFileName(self, name):
        self.fileName = name
        return True
    ##############################################################################

    ##############################################################################
    def set_exposure(self, exposure_time_seg):
        self.sendMessage(f'SET EXPOSURE {exposure_time_seg}')
        data = self.getMessage()
        if data == 'OK':
            return True
        self.printError(data)
        return False
    ##############################################################################

    ##############################################################################
    def change_binningRuntime(self, bx, by):
        self.sendMessage(f'CHANGE BINNING {bx} {by}')
        data = self.getMessage()
        if data == 'OK':
            return True
        self.printError(data)
        return False
    ##############################################################################

    ##############################################################################
    def auto_exposureSaturation(self, saturated_fractionGoal=0.05, fraction_tolerance=0.01, single_channel=False):
        single_channel_value = 1 if single_channel else 0
        self.sendMessage(f'AUTO EXPOSURE SATURATION {saturated_fractionGoal} {fraction_tolerance} {single_channel_value}')
        data = self.getMessage()
        words = data.split()
        if len(words) == 5 and words[0] == 'OK' and words[1] == 'EXPOSURE' and words[3] == 'SATURATION':
            return float(words[2]), float(words[4])
        self.printError(data)
        return None
    ##############################################################################

    ##############################################################################
    def start_autofocusAcquisition(self, max_photos=100, time_photo=0.2):
        self.sendMessage(f'START AUTOFOCUS ACQUISITION {max_photos} {time_photo}')
        data = self.getMessage()
        if data == 'OK':
            return True
        self.printError(data)
        return False
    ##############################################################################

    ##############################################################################
    def stop_autofocusAcquisition(self):
        self.sendMessage('STOP AUTOFOCUS ACQUISITION')
        data = self.getMessage()
        words = data.split()
        if len(words) == 5 and words[0] == 'OK' and words[1] == 'N' and words[3] == 'LIMIT':
            return {
                'n': int(words[2]),
                'reached_max_photos': bool(int(words[4])),
                'best_index': None,
                'best_sharpness': None,
                'best_time': None,
            }
        if (
            len(words) == 11
            and words[0] == 'OK'
            and words[1] == 'N'
            and words[3] == 'LIMIT'
            and words[5] == 'BEST_INDEX'
            and words[7] == 'BEST_SHARPNESS'
            and words[9] == 'BEST_TIME'
        ):
            return {
                'n': int(words[2]),
                'reached_max_photos': bool(int(words[4])),
                'best_index': int(words[6]),
                'best_sharpness': float(words[8]),
                'best_time': float(words[10]),
            }
        self.printError(data)
        return None
    ##############################################################################

    ##############################################################################
    def stop(self):
        self.sendMessage('STOP')
        self.exit()

    ##############################################################################
    def getHolePosition(self):

        return np.asarray([0,0])

    ##############################################################################
    def getCalibrationHole(self):

        self.takePic()
        
        #Function that implements here the coordinates of the hole in 2D
        point2D = getHolePosition()
        if not point2D:
            printError('None hole was found in this camera position')
            return point2D
        point3D = self.robot3D.cameraProjectionToPoint3D(point2D)
        return point3D

    ##############################################################################
    def takePic(self):

        self.printLog('Requesting a picture to the server')
        self.sendMessage('TAKE PICTURE')
        data = self.getMessage()
        words = data.split()
        fileName = ''
        fileSize = ''
        if words[0] == 'FILE:' and words[2] == 'SIZE:':
            fileName = words[1]
            fileSize = words[3]
            self.printLog('Transfering file: ' + fileName + ' with size ' + fileSize + ' bytes')
            self.getFile(fileName, int(fileSize))
            self.sendMessage('OK')
        else:
            self.printError('There was an error with the file information')
            self.exit()
    ##############################################################################    

    ##############################################################################
    def handshake(self):
        
        self.printLog('Starting handshake')
        self.sendMessage('HI SERVER')
        
        data = self.getMessage()
        if data == 'HI CLIENT':
            self.printLog('Server says ' + data)
            self.sendMessage('HANDSHAKE CONFIRMED')
            return True
        else:
            self.printError('Server Handshake response is not valid')
            self.exit()
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
        self.s.shutdown(socket.SHUT_RDWR)
        self.s.close()
        sys.exit()
    ##############################################################################

    ##############################################################################
    def showBanner(self):

        print( self.HEADER)  
        print(' _____                                  _____ _ _            _              ')
        print('/ ____|                                / ____| (_)          | |             ') 
        print('| |     __ _ _ __ ___   ___ _ __ __ _  | |    | |_  ___ _ __ | |_           ')
        print('| |    / _` | \'_ ` _ \\ / _ \\ \'__/ _` | | |    | | |/ _ \\ \'_ \\| __|   ')
        print('| |___| (_| | | | | | |  __/ | | (_| | | |____| | |  __/ | | | |_           ')
        print('\\______\\__,_|_| |_| |_|\\___|_|  \\__,_|  \\_____|_|_|\\___|_| |_|\\__|    ')                                                   
        print( self.ENDC)
        print( '\n\n')
    ##############################################################################

    ##############################################################################
    def getMessage(self):

        counter = 0
        text = ''
        while True:
            msg = self.s.recv(512)
            text = text + msg.decode()
            counter = counter + len(msg)
            if counter == 512:
                break
        return text[0:text.find('XXXXX')]
    #############################################################################

    ##############################################################################
    def sendMessage(self, msg):

        if len(msg) >= 512-5:
            return False 
        for i in range(len(msg), 512):
            msg += 'X'
        self.s.sendall(msg.encode())
        return True
    ##############################################################################

    ##############################################################################
    def getFile(self, filename, filesize):

        f = open(self.fileName, 'wb')
        counter = 0
        while True:
            l = self.s.recv(2048)
            counter = counter + len(l)
            f.write(l)
            if counter == filesize:
                break
        f.close()
    ##############################################################################
  
