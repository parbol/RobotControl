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

class RobotController:

    ##############################################################################
    def __init__(self, device, bauds):

        #Technical stuff
        self.HEADER = '\033[95m'
        self.OKBLUE = '\033[94m'
        self.OKGREEN = '\033[92m'
        self.FAIL = '\033[91m'
        self.ENDC = '\033[0m'
        
        #Information for the client
        self.device = device
        self.bauds = bauds

        #Show off
        self.showBanner()

        #Create connection
        self.serial = serial.Serial(self.device, self.bauds, timeout=1)
        self.serial.open()

        self.printLog('Connection established')

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
            msg = self.serial.rad(512)
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
        self.serial.write(msg.encode())
        return True
    ##############################################################################

  
    ##############################################################################
    def goTo(self, x, y, z, v):

        xs = str(x)
        ys = str(y)
        zs = str(z)
        vx = str(z)
        if x >= 0:
            xs = '+' + xs
        if y >= 0:
            ys = '+' + ys
        if z >= 0:
            zs = '+' + zs
        if v >= 0:
            vs = '+' + vs

        cadena = f'GOTO:{xs}{ys}{zs}{vs})'
        
        sel.sendMessage(cadena)
        data = self.getMessage()
        if data == 'OK':
            return True
        else:
            self.printError('Unexpected message from CS9')
            sys.exit()
        return True
    ##############################################################################

  

