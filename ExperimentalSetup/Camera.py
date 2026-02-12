import numpy as np
from src.EulerRotation import EulerRotation

class Camera:

    def __init__(self, x, y, z, psi, theta, phi, cx, cy, focaldistance, sigmaCamera):

        self.r0 = np.asarray([x, y, z])
        self.rotation0 = EulerRotation(psi, theta, phi)
        self.sigmaCamera = sigmaCamera
        self.cx = cx
        self.cy = cy
        self.focaldistance = focaldistance
        self.r0global = np.asarray([0.0, 0.0, 0.0])
        self.uxglobal = np.asarray([1.0, 0.0, 0.0])
        self.uyglobal = np.asarray([0.0, 1.0, 0.0])
        self.uzglobal = np.asarray([0.0, 0.0, 1.0])


    def setCameraGlobalInformation(self, r0global, uxglobal, uyglobal, uzglobal):
        
        self.r0global = r0global
        self.uxglobal = uxglobal
        self.uyglobal = uyglobal
        self.uzglobal = uzglobal




       