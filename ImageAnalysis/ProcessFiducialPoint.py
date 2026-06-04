import cv2
import numpy as np
from matplotlib import pyplot as plt
import math


class ProcessFiducialPoint:

    def __init__(self, imageName):

        self.imageName = imageName
        self.height = 0
        self.width = 0
        #Technical stuff
        self.HEADER = '\033[95m'
        self.OKBLUE = '\033[94m'
        self.OKGREEN = '\033[92m'
        self.FAIL = '\033[91m'
        self.ENDC = '\033[0m'
        self.WARNING = '\033[93m'
        self.printLog('Start calibration point')

    def fit(self):
        
        self.printLog('Starting the fit with image ' + self.imageName)
        
        #Figure 
        fig, axs = plt.subplots(1, 3, figsize=(20, 10))
        
        #Reading and transforming image
        img = cv2.imread(self.imageName)
        self.img_height, self.img_width = img.shape[:2]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        axs[0].imshow(gray, cmap='gray')
        axs[0].set_title('Original image')
       
        #Getting the main contour
        _, thresh = cv2.threshold(gray, 60, 255, cv2.THRESH_BINARY)
        axs[1].imshow(thresh, cmap='gray')
        axs[1].set_title('Thresholded image')
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        contourssorted = sorted(contours, key=cv2.contourArea, reverse=True)
        print(f"Found {len(contours)} contours")

        for i, c in enumerate(contourssorted):
            print(f"Contour {i}: area = {cv2.contourArea(c):.1f}")

        discarded_label = False
        for i, c in enumerate(contourssorted):
            if cv2.contourArea(c) < 1:
                continue
            c = c.squeeze()
            if i == 0:
                axs[1].plot(c[:,0], c[:,1], 'g', linewidth=2, label="Selected contour")
            else:
                if not discarded_label:
                    axs[1].plot(c[:,0], c[:,1], 'r', linewidth=2, label="Discarded contours")
                    discarded_label = True
                else:
                    axs[1].plot(c[:,0], c[:,1], 'r', linewidth=2)
        axs[1].legend()
        
        contourselected = contourssorted[0]
        valid = self.checkConsistency(contourselected)
        
        if not valid:
            self.printError('Pattern recognition unsuccessfull')
            return 0, 0, False

        x, y, valid = self.estimateDistances(contourselected)
        
        # Drawing final
        circle = plt.Circle((x,y), 10, color='red', fill=True)
        axs[2].add_patch(circle)
        axs[2].imshow(gray, cmap='gray')
        axs[2].set_title('Final estimate')
        plt.show()
        return x, y, valid


    ##############################################################################
    def checkConsistency(self, c):
        area = cv2.contourArea(c)
        if area < 100000.0 or area > 400000.0:
            return False
        return True

    ##############################################################################
    
    ##############################################################################
    def estimateDistances(self, c):
        M = cv2.moments(c)
        if M["m00"] == 0:
            return 0, 0, False
        x = int(M['m10']/M['m00'])
        y = int(M['m01']/M['m00'])
        return x, y, True


    ##############################################################################
    ##############################################################################
    def is_on_border(self, x, y):
        
        if (x == 0 or x == 1 or x == self.img_width - 2 or x == self.img_width - 1) or (y == 0 or y == 1 or y == self.img_height -2 or y == self.img_height - 1):
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

