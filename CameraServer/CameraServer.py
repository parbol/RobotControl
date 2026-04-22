#   ______                                   _____                          
#  / ____/___ _____ ___  ___  _________ _   / ___/___  ______   _____  _____
# / /   / __ `/ __ `__ \/ _ \/ ___/ __ `/   \__ \/ _ \/ ___/ | / / _ \/ ___/
#/ /___/ /_/ / / / / / /  __/ /  / /_/ /   ___/ /  __/ /   | |/ /  __/ /    
#\____/\__,_/_/ /_/ /_/\___/_/   \__,_/   /____/\___/_/    |___/\___/_/     
#
import socket
import sys
import time
import os
import math

from PIL import Image



class CameraServer:

    ##############################################################################
    def __init__(self, robot_IP, robot_PORT, camera):

        #Technical stuff
        self.HEADER = '\033[95m'
        self.OKBLUE = '\033[94m'
        self.OKGREEN = '\033[92m'
        self.FAIL = '\033[91m'
        self.ENDC = '\033[0m'

        #Camera controler
        self.camera = camera

        #Information for the client
        self.robot_IP = robot_IP
        self.robot_PORT = robot_PORT

        #Picture name
        self.pictureName = camera.filename

        self.showBanner()
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #Create connection
        server_address = (self.robot_IP, self.robot_PORT)
        self.s.bind(server_address)
        self.s.listen(1)    
        while True:       
           
            self.printLog('The server is listening')
            self.connection, self.client_address = self.s.accept()
            self.printLog('Connection request from: ' + self.client_address[0] + ' using port: ' + str(robot_PORT))

            try:
                #Start the server action
                if not self.handleHandshake():
                    self.s.close()
                    continue
                while True:
                    if not self.handleCommand():
                        self.connection.close()
                        break
            except:
                self.printError('Unexpected error ocurred')
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

        self.s.shutdown(socket.SHUT_RDWR)
        self.s.close()
        sys.exit(0)
    ##############################################################################
 
    ##############################################################################
    def showBanner(self):

        print(self.HEADER)
        print(' ______                                   _____                          ')
        print('/ ____/___ _____ ___  ___  _________ _   / ___/___  ______   _____  _____  ')
        print('/ /   / __ `/ __ `__ \\/ _ \\/ ___/ __ `/   \\__ \\/ _ \\/ ___/ | / / _ \\/ ___/ ')
        print('/ /___/ /_/ / / / / / /  __/ /  / /_/ /   ___/ /  __/ /   | |/ /  __/ /    ')
        print('\\____/\\__,_/_/ /_/ /_/\\___/_/   \\__,_/   /____/\\___/_/    |___/\\___/_/     ')
        print(self.ENDC)
        print('\n\n')
    ##############################################################################

    ##############################################################################
    def getMessage(self):

        counter = 0
        text = ''
        while True:
            msg = self.connection.recv(512)
            text = text + msg.decode()
            counter = counter + len(msg)
            if counter == 512:
                break
        return text[0:text.find('XXXXX')]
    ##############################################################################

    ##############################################################################
    def sendMessage(self, msg):

        if len(msg) >= 512-5:
            return False 
        for i in range(len(msg), 512):
            msg += 'X'
        self.connection.sendall(msg.encode())
        return True
    ##############################################################################

    ##############################################################################
    def handleHandshake(self):

        data = self.getMessage() 
        if data == 'HI SERVER':
            self.printLog('Client says: ' + data)
        else: 
            self.printError("The handshake was not successful")
            return False

        #First handshake message 
        self.sendMessage('HI CLIENT')
        data = self.getMessage()
        if data == 'HANDSHAKE CONFIRMED':
            self.printLog('Client says: ' + data)
        else:
            self.printError("The HANDSHAKE was not finished")
            return False

        self.printLog("Handshake was correct") 
        return True
    ##############################################################################

    ##############################################################################
    def handleCommand(self):

        data = self.getMessage() 
        if data == 'STOP':
            self.printLog('Client says: ' + data)
            self.printLog('Closing connection with client')
            return False
        elif data == 'TAKE PICTURE': 
            self.printLog('Client says: ' + data)
            return self.handlePicture()
        elif data.startswith('SET EXPOSURE'):
            self.printLog('Client says: ' + data)
            return self.handle_setExposure(data)
        elif data.startswith('CHANGE BINNING'):
            self.printLog('Client says: ' + data)
            return self.handle_changeBinningRuntime(data)
        elif data.startswith('AUTO EXPOSURE SATURATION'):
            self.printLog('Client says: ' + data)
            return self.handle_autoExposureSaturation(data)
        elif data.startswith('START AUTOFOCUS ACQUISITION'):
            self.printLog('Client says: ' + data)
            return self.handle_startAutofocusAcquisition(data)
        elif data.startswith('STOP AUTOFOCUS ACQUISITION'):
            self.printLog('Client says: ' + data)
            return self.handle_stopAutofocusAcquisition(data)
        else:
            self.printError("Unexpected command received")
            return False
        return True
    ##############################################################################

    ##############################################################################
    def handle_setExposure(self, data):
        words = data.split()
        if len(words) != 3:
            self.sendMessage('ERROR: SET EXPOSURE requires one value')
            return True
        try:
            exposure_time_seg = float(words[2])
            self.camera.set_exposure(exposure_time_seg)
        except Exception as e:
            self.sendMessage('ERROR: ' + str(e))
            return True
        self.sendMessage('OK')
        return True
    ##############################################################################

    ##############################################################################
    def handle_changeBinningRuntime(self, data):
        words = data.split()
        if len(words) != 4:
            self.sendMessage('ERROR: CHANGE BINNING requires bx and by')
            return True
        try:
            bx = int(words[2])
            by = int(words[3])
            if not self.camera.change_binningRuntime(bx, by):
                self.sendMessage('ERROR: binning was not applied')
                return True
        except Exception as e:
            self.sendMessage('ERROR: ' + str(e))
            return True
        self.sendMessage('OK')
        return True
    ##############################################################################

    ##############################################################################
    def handle_autoExposureSaturation(self, data):
        words = data.split()
        if len(words) != 6:
            self.sendMessage('ERROR: AUTO EXPOSURE SATURATION requires goal tolerance single_channel')
            return True
        try:
            saturated_fractionGoal = float(words[3])
            fraction_tolerance = float(words[4])
            single_channel = bool(int(words[5]))
            result = self.camera.auto_exposureSaturation(
                saturated_fractionGoal,
                fraction_tolerance,
                single_channel,
            )
            if result is None:
                self.sendMessage('ERROR: auto exposure saturation failed')
                return True
            exposure_time_seg, saturated_fraction = result
        except Exception as e:
            self.sendMessage('ERROR: ' + str(e))
            return True
        self.sendMessage(f'OK EXPOSURE {exposure_time_seg} SATURATION {saturated_fraction}')
        return True
    ##############################################################################

    ##############################################################################
    def handle_startAutofocusAcquisition(self, data):
        words = data.split()
        if len(words) != 5:
            self.sendMessage('ERROR: START AUTOFOCUS ACQUISITION requires max_photos dead_time')
            return True
        try:
            max_photos = int(words[3])
            dead_time = float(words[4])
            if not self.camera.start_autofocusAcquisition(max_photos, dead_time):
                self.sendMessage('ERROR: autofocus acquisition already running')
                return True
        except Exception as e:
            self.sendMessage('ERROR: ' + str(e))
            return True
        self.sendMessage('OK')
        return True
    ##############################################################################

    ##############################################################################
    def handle_stopAutofocusAcquisition(self, data):
        words = data.split()
        if len(words) != 3:
            self.sendMessage('ERROR: STOP AUTOFOCUS ACQUISITION does not take arguments')
            return True
        try:
            sharp_array, time_stamps = self.camera.stop_autofocusAcquisition()
            n_points = len(sharp_array)
            if n_points == 0:
                self.sendMessage('OK N 0')
                return True
            best_index = max(range(n_points), key=lambda i: sharp_array[i])
            self.sendMessage(
                f'OK N {n_points} BEST_INDEX {best_index} '
                f'BEST_SHARPNESS {sharp_array[best_index]} BEST_TIME {time_stamps[best_index]}'
            )
        except Exception as e:
            self.sendMessage('ERROR: ' + str(e))
            return True
        return True
    ##############################################################################

    ##############################################################################
    def handlePicture(self):

        #self.takeTheActualPicture()
        self.printLog('Client has requested a picture')
        
        #This should be taking the picture
        self.camera.get_image()
        picture = self.camera.image
        picture.save(self.pictureName, "PNG")
        try:
            filesize = os.path.getsize(self.pictureName)
        except:
            self.printError('Image file does not exist')
            self.exit()
        self.printLog('Sending file: ' + self.pictureName + ' of size: ' + str(filesize) + ' bytes')
        self.sendMessage(f'FILE: {self.pictureName} SIZE: {str(filesize)}')
        #Aqui deberia mandar el archivo
        self.sendFile(self.pictureName, filesize)
        data = self.getMessage()
        if data == 'OK':
            self.printLog('Client says ' + data)
            self.printLog('File transferred successfully')
        else:
            self.printError('Unexpected error in the transfer')
            return False
        return True
    ##############################################################################
      
    ##############################################################################
    def sendFile(self, filename, filesize):

        f = open(self.pictureName, 'rb')
        nrows = math.floor(filesize/2048)
        extra = filesize % 2048
        for i in range(0, nrows):
            l = f.read(2048)
            self.connection.sendall(l)
        l = f.read(extra)
        self.connection.sendall(l)
        f.close()
    ##############################################################################
