import numpy as np
from ExperimentalSetup.EulerRotation import EulerRotation


class Camera:

    def __init__(self, x, y, z, psi, theta, phi, cx, cy, focaldistance, focusdistance):

        #This is the position of the camera with respect to the system of arm2
        self.r0 = np.asarray([x, y, z])
        self.rotation0 = EulerRotation(psi, theta, phi)
        self.npixelx = 2064
        self.npixely = 1544
        self.psi = psi
        self.theta = theta
        self.phi = phi
        self.cx = cx
        self.cy = cy
        self.focaldistance = focaldistance 
        self.focusdistance = focusdistance
        # r0 global, uxglobal, uyglobal, uz global ?
        self.r = np.asarray([0, 0, 0])
        self.ux = np.asarray([1.0, 0.0, 0.0])
        self.uy = np.asarray([0.0, 1.0, 0.0])
        self.uz = np.asarray([0.0, 0.0, 1.0])
      

    def update(self):

        self.rotation0 = EulerRotation(self.psi, self.theta, self.phi)