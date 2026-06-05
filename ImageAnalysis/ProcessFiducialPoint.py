import cv2
import numpy as np
from matplotlib import pyplot as plt
import math


class ProcessFiducialPoint:

    def __init__(self, imageName, is_ETROC):

        self.imageName = imageName
        self.is_ETROC = is_ETROC
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

    def selectContour_ETROC(self):
        self.printLog('Starting the fit with image ' + self.imageName)
        
        
        #Reading and transforming image
        img = cv2.imread(self.imageName)
        self.img_height, self.img_width = img.shape[:2]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        #Getting contours
        _, thresh = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        contourssorted = sorted(contours, key=cv2.contourArea, reverse=True)
        # First contour is whole image
        # Second is the whole Fiducial mark (also possible to obtain center of mass)
        # Select 3,4,5,6 wich are the inner circles
        contoursselected = contourssorted[2:6]

        return contoursselected, contourssorted, gray, thresh

    def selectContour_PCB(self):
        self.printLog('Starting the fit with image ' + self.imageName)
        
        
        #Reading and transforming image
        img = cv2.imread(self.imageName)
        self.img_height, self.img_width = img.shape[:2]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        #Getting contours
        _, thresh = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        contourssorted = sorted(contours, key=cv2.contourArea, reverse=True)
        # First is the whole Fiducial mark (also possible to obtain center of mass)
        # Select 2,3,4,5 wich are the inner circles
        contoursselected = contourssorted[1:5]

        return contoursselected, contourssorted, gray, thresh

    def fit(self):
        # Get contours
        if self.is_ETROC:
            contoursselected, contourssorted, gray, thresh = self.selectContour_ETROC()
        else:
            contoursselected, contourssorted, gray, thresh = self.selectContour_PCB()


        #Figure 
        fig, axs = plt.subplots(1, 3, figsize=(20, 10))
        # Draw image
        axs[0].imshow(gray, cmap='gray')
        axs[0].set_title('Original image')
        # Draw binary image with contours
        axs[1].imshow(thresh, cmap='gray')
        axs[1].set_title('Thresholded image')
        
        _is_first_contour = True
        for i, c in enumerate(contourssorted):
            # Skip small contours
            if cv2.contourArea(c) < 50:
                continue
            c = c.squeeze()
            if _is_first_contour:
                axs[1].plot(c[:,0], c[:,1], 'r', linewidth=2, label="Discarded contours")
                _is_first_contour = False
            else:
                axs[1].plot(c[:,0], c[:,1], 'r', linewidth=2)

        _is_first_contour = True
        for i, c in enumerate(contoursselected):
            c = c.squeeze()
            if _is_first_contour:
                axs[1].plot(c[:,0], c[:,1], 'g', linewidth=2, label="Selected contours")
                _is_first_contour = False
            else:
                axs[1].plot(c[:,0], c[:,1], 'g', linewidth=2)
        axs[1].legend()
        
        valid = self.checkConsistency(contoursselected)
        
        if not valid:
            plt.show()
            self.printError('Pattern recognition unsuccessfull')
            return 0, 0, False

        arrayx, arrayy, x, y, d, valid = self.estimateDistances(contoursselected)
        
        # Drawing final
        circle = plt.Circle((x,y), 10, color='green', fill=True)
        axs[2].add_patch(circle)
        axs[2].imshow(gray, cmap='gray')
        axs[2].set_title('Final estimate')
        plt.plot(arrayx, arrayy, color='red')
        plt.savefig(f"Fit_{self.imageName}")
        return x, y, valid

    ##############################################################################
    def checkConsistency(self, c):
        for i in range(len(c)):
            area = cv2.contourArea(c[i])
            if area < 10000.0 or area > 40000.0:
                print(f"Not right area {area}")
                return False
        return True

    ##############################################################################
    
    ##############################################################################
    def estimateDistances(self, c):

        x = []
        y = []
        for i in range(len(c)):
            M = cv2.moments(c[i])
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            x.append(cx)
            y.append(cy)

        xc = np.mean(np.asarray(x))
        yc = np.mean(np.asarray(y))
        d = []
        for i in range(4):
            for j in range(4):
                if i == j:
                    continue
                d.append(math.sqrt((x[i]-x[j])**2 + (y[i]-y[j])**2))
        dsorted = sorted(d, reverse=True)
        dmean = 0
        for i in range(4):
            dmean += dsorted[i]
        dmean = dmean/4.0
        #This is needed for drawing purposes
        x.append(x[0])
        y.append(y[0])
        return x, y, xc, yc, dmean, True

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

