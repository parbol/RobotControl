import cv2
import numpy as np
from matplotlib import pyplot as plt
from ImageAnalysis.CircleFitter import CircleFitter
import math


class ProcessCalibrationPoint:

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
        _, thresh = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        largest_contour = max(contours, key=cv2.contourArea)
        xv = []
        yv = []
        filteredpoints = []
        for p in largest_contour:
            x, y = p[0]
            if not self.is_on_border(x, y):
                filteredpoints.append([[x, y]])
                xv.append(x)
                yv.append(y)

        #Drawing the main contour
        filteredpoints = np.array(filteredpoints, dtype=np.int32)
        mask = np.zeros_like(gray)
        cv2.drawContours(mask, [filteredpoints], -1, 255, -1)
        background = np.ones_like(img) * 255
        final = np.where(mask[:,:,None] == 255, img, background)
        axs[1].imshow(final, cmap='gray')
        axs[1].set_title('Contour selection')

        #Making the fit
        results = []
        try:
            cal = CircleFitter(xv, yv)
            results = cal.fit()
        except:
            return 0, 0, False

        a, b, r = results.params
        print(f"Centro del círculo: (x={a}, y={b}), radius={r}")
        
        xv2, yv2 = self.checkMinError(a, b, r, xv, yv)
        results2 = []
        try:
            cal2 = CircleFitter(xv2, yv2)
            results2 = cal2.fit()
        except:
            return 0, 0, False

        a, b, r = results2.params
        print(f"Centro del círculo: (x={a}, y={b}), radius={r}")
        
        #Drawing final
        circle = plt.Circle((a,b), r, color='blue', fill='false')
        axs[2].add_patch(circle)
        axs[2].imshow(final, cmap='gray')
        axs[2].set_title('Final circle')
        plt.show()
        return a, b, True


    def checkMinError(self, a, b, r, xv, yv):

        d = 0
        maxd = 0
        for i in range(len(xv)):
            phi = math.atan2(yv[i]-b, xv[i]-a)
            x = a + r * math.cos(phi)
            y = b + r * math.sin(phi)
            di = math.sqrt((xv[i]-x)**2 + (yv[i]-y)**2)
            if di > maxd:
                maxd = di
            d = d + di
        d = d / len(xv)
        xv2 = []
        yv2 = []
        for i in range(len(xv)):
            phi = math.atan2(yv[i]-b, xv[i]-a)
            x = a + r * math.cos(phi)
            y = b + r * math.sin(phi)
            di = math.sqrt((xv[i]-x)**2 + (yv[i]-y)**2)
            if di < 2.0*d:
                xv2.append(xv[i])
                yv2.append(yv[i])
        return xv2, yv2


    def is_on_border(self, x, y):
        
        if (x == 0 or x == 1 or x == self.img_width - 2 or x == self.img_width - 1) or (y == 0 or y == 1 or y == self.img_height -2 or y == self.img_height - 1):
            return True
        else:
            return False

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

