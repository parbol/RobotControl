import cv2
import numpy as np
from matplotlib import pyplot as plt
from ImageAnalysis.CircleFitter import CircleFitter



class ProcessCalibrationPoint:

    def __init__(self, imageName):

        self.imageName = imageName
        self.height = 0
        self.width = 0

    def fit(self):
        
        img = cv2.imread(self.imageName)
        self.img_height, self.img_width = img.shape[:2]

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
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

        cal = CircleFitter(xv, yv)
        results = cal.fit()

        print(results.summary())
        print(results.params)
        a, b, r = results.params

        filteredpoints = np.array(filteredpoints, dtype=np.int32)
        mask = np.zeros_like(gray)
        cv2.drawContours(mask, [filteredpoints], -1, 255, -1)

        # Crear fondo blanco
        background = np.ones_like(img) * 255
        final = np.where(mask[:,:,None] == 255, img, background)
        fig2, ax2 = plt.subplots(figsize=(20, 20))
        ax2.imshow(final, cmap='gray')
        circle = plt.Circle((a,b), r, color='blue', fill='false')
        ax2.add_patch(circle)
        ax2.axis('off')
        plt.show()
        print(f"Centro del círculo: (x={cx}, y={cy})")
        print(f"Centro del círculo: (x={a}, y={b}), radius={r}")


    def is_on_border(self, x, y):
        
        if (x == 0 or x == 1 or x == self.img_width - 2 or x == self.img_width - 1) or (y == 0 or y == 1 or y == self.img_height -2 or y == self.img_height - 1):
            return True
        else:
            return False


