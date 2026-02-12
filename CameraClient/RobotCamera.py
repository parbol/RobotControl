import socket
import time
import sys
import os
import math

class RobotCamera:

    ##############################################################################
    def __init__(self, robot_IP, robot_PORT, filenameInput):

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
    def stop(self):
        self.sendMessage('STOP')
        self.exit()


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
  
