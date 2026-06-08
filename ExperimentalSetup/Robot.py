##############################################################
##############################################################
######################## Robot program #######################
##############################################################
##############################################################

import numpy as np
import random
import sys
import math as math
from ExperimentalSetup.Camera import Camera
from ExperimentalSetup.EulerRotation import EulerRotation
from ExperimentalSetup.Table import Table

import logging
logger = logging.getLogger(__name__)

logging.basicConfig(format="{asctime} - {levelname} - {message}", style="{", datefmt="%Y-%m-%d %H:%M", level=logging.ERROR)  # level=logging.INFO o level=logging.ERROR



####################################################################
# Some definitions                                                 #
# The robot pointer has two systems of coordinates:                #
# Cartesian: (x, y, z) and JZ = position of the pointer and JZ     #
# Inner: (J1, J2, Z) and JZ = rotations of the axis                #
# The robot pointer position z is Z0 - Z                           #
####################################################################
# The robot has also two imporant systems of reference:            #
# The absolute one with respect to the table (x, y, z)             # 
# And the one associated to the second arm of the robot            # 
# with the center at the robot pointer                             #
####################################################################


class Robot:

    def __init__(self, R1, R2, Z0, table, camera):

        #Robot parameters
        self.R1 = R1
        self.R2 = R2
        #Z0 is the height of the pointer of the robot when Z = 0
        self.Z0 = Z0
        self.tol = 1e-3
        # logging.info(f'Robot R1: {R1}, R2: {R2}, h: {h}, Z0: {Z0} tol: {self.tol}')
        #Camera and table
        self.camera = camera
        self.table = table
        #Current position in cartesian coordinates
        self.position = np.asarray([0.0, 0.0, 0.0])
        self.ux = np.asarray([1.0, 0.0, 0.0])
        self.uy = np.asarray([0.0, 1.0, 0.0])
        self.uz = np.asarray([0.0, 0.0, 1.0])
        #Current position in J coordinates
        self.J1 = 0
        self.J2 = 0
        self.J3 = 0
        self.J4 = 0
        #Rotation needed for the Jz motion
        self.jzrot = EulerRotation(0.0, 0.0, 0.0)
        #This is the definition of the field of the camera
        self.frame = [np.asarray([0.0, 0.0, 0.0]), np.asarray([0.0, 0.0, 0.0]), np.asarray([0.0, 0.0, 0.0]), np.asarray([0.0, 0.0, 0.0])]
        self.N = 0

    ######### Move the robot ###########################################
    def JMoveRobotTo(self, pos):
        
        #Update the J coordinates
        self.J1 = pos[0] 
        self.J2 = pos[1] 
        self.J3 = pos[2] 
        self.J4 = -pos[3] 
        self.jzrot.setFromAngles(self.J4, 0.0, 0.0)

        #Update the cartesian coordinates
        self.updateCartesian()

        # logging.info(f'Moving robot to J1: {pos.J1}, J2: {pos.J2}, Z: {pos.Z}, JZ: {pos.Jz}')
        # logging.info(f'Moving robot to x: {self.currentCartesianPos.r[0]}, y: {self.currentCartesianPos.r[1]}, z: {self.currentCartesianPos.r[2]}')
        #Update the position of the camera
        self.updateCamera()

    
    ######### Move the robot ###########################################
    def CartesianMoveRobotTo(self, pos, refJ):

        status, j1, j2, Z = self.fromCartesianToInner(np.asarray([pos[0], pos[1], pos[2]]))
        self.J4 = pos[3]  
        self.jzrot.setFromAngles(pos.J4, 0.0, 0.0)
        
        
        if status:
            pos = innerpoint(j1, j2, Z, jz)
            self.MoveRobotTo(pos)
        else:
            r = np.sqrt(v[0]**2 + v[1]**2)
            logging.error(f'There was an error moving the robot. R = {r}')
            sys.exit()     

   
    ######### Set camera globals #######################################
    def updateCamera(self):
       
        robotPointerToCamera = self.camera.r0[0] * self.ux + self.camera.r0[1] * self.uy + self.camera.r0[2] * self.uz
        self.camera.r = self.position + self.jzrot.apply(robotPointerToCamera)      
        #self.camera.ux = self.camera.r - self.position
        #self.camera.ux = self.camera.ux/np.linalg.norm(self.camera.ux)
        #self.camera.uz = self.uz
        #self.camera.uy = np.cross(self.camera.uz, self.camera.ux)
        self.camera.ux = self.jzrot.apply(self.ux)
        self.camera.uy = self.jzrot.apply(self.uy)
        self.camera.uz = self.jzrot.apply(self.uz)
        self.camera.ux = self.camera.rotation0.apply(self.camera.ux)
        self.camera.uy = self.camera.rotation0.apply(self.camera.uy)
        self.camera.uz = self.camera.rotation0.apply(self.camera.uz)
        # logging.info(f'Moving camera to x: {self.camera.cartesianpos.r[0]}, y: {self.camera.cartesianpos.r[1]}, z: {self.camera.cartesianpos.r[2]}')
        # logging.info(f'Camera ux vector: ({self.camera.cartesianpos.ux[0]}, {self.camera.cartesianpos.ux[1]}, {self.camera.cartesianpos.ux[2]})')
        # logging.info(f'Camera uy vector: ({self.camera.cartesianpos.uy[0]}, {self.camera.cartesianpos.uy[1]}, {self.camera.cartesianpos.uy[2]})')
        # logging.info(f'Camera uz vector: ({self.camera.cartesianpos.uz[0]}, {self.camera.cartesianpos.uz[1]}, {self.camera.cartesianpos.uz[2]})')
        p1 = [1.0 ,  1.0]
        p2 = [1.0 , -1.0]
        p3 = [-1.0, -1.0]
        p4 = [-1.0,  1.0]
        self.frame[0] = self.cameraProjectionToPoint3D(p1)
        self.frame[1] = self.cameraProjectionToPoint3D(p2)
        self.frame[2] = self.cameraProjectionToPoint3D(p3)
        self.frame[3] = self.cameraProjectionToPoint3D(p4)


    ######### Set Check if a point is within the frame##################  
    def checkInFrame(self, p):
        
        x, y = self.point3DToCameraProjection(p)
        if x >= -1.0 and x <= 1.0 and y >= -1.0 and y <= 1.0:
            return True
        return False

    ######## Auxiliary function##########################################
    def angleFromSineCosine(self, s, c):

        if s >= 0:
            return np.arccos(c)
        else:
            return -np.arccos(c)


    #Auxiliary function to check whether two points are the same##########
    def checkValidConversion(self, v, j):

        x = self.R1 * np.cos(j[0]) + self.R2 * np.cos(j[1])
        y = self.R1 * np.sin(j[0]) + self.R2 * np.sin(j[1])
        if (x-v[0])**2 + (y-v[1])**2 < self.tol:
            return True
        return False


    ######################################################################
    def updateCartesian(self):

        x = self.R1 * np.cos(self.J1) + self.R2 * np.cos(self.J2+self.J1)
        y = self.R1 * np.sin(self.J1) + self.R2 * np.sin(self.J2+self.J1)
        z = self.J3

        self.position = np.asarray([x, y, z])
        self.ux = np.asarray([np.cos(self.J1+self.J2), np.sin(self.J1+self.J2), 0.0])
        self.uy = np.asarray([-np.sin(self.J1+self.J2), np.cos(self.J1+self.J2), 0.0])
        self.uz = np.asarray([0.0, 0.0, 1.0])


    ######################################################################
    def fromCartesianToInner(self, v):

        x = v[0]  
        y = v[1] 
        z = v[2] 
        Z = z
        Delta = (x**2 + y**2 + self.R1**2 - self.R2**2)/(2.0*self.R1)
        a = (x**2 + y**2)
        b = -2.0 * Delta * x
        c = Delta**2 - y**2

        if b**2-4.0*a*c < 0.0:
            return False, 0, 0, 0
    
        cosj1_p = (-b + np.sqrt(b**2-4.0*a*c))/(2.0*a)
        cosj2_p = (x - self.R1 * cosj1_p) / self.R2
        sinj1_pp = np.sqrt(1.0 - cosj1_p**2)
        sinj2_pp = (y - self.R1 * sinj1_pp) / self.R2
        sinj1_pm = -np.sqrt(1.0 - cosj1_p**2)
        sinj2_pm = (y - self.R1 * sinj1_pm) / self.R2

        cosj1_m = (-b - np.sqrt(b**2-4.0*a*c))/(2.0*a)
        cosj2_m = (x - self.R1 * cosj1_m) / self.R2
        sinj1_mp = np.sqrt(1.0 - cosj1_m**2)
        sinj2_mp = (y - self.R1 * sinj1_mp) / self.R2
        sinj1_mm = -np.sqrt(1.0 - cosj1_m**2)
        sinj2_mm = (y - self.R1 * sinj1_mm) / self.R2

        J1pp = self.angleFromSineCosine(sinj1_pp, cosj1_p)
        J1pm = self.angleFromSineCosine(sinj1_pm, cosj1_p)
        J1mp = self.angleFromSineCosine(sinj1_mp, cosj1_m)
        J1mm = self.angleFromSineCosine(sinj1_mm, cosj1_m)
        J2pp = self.angleFromSineCosine(sinj2_pp, cosj2_p)
        J2pm = self.angleFromSineCosine(sinj2_pm, cosj2_p)
        J2mp = self.angleFromSineCosine(sinj2_mp, cosj2_m)
        J2mm = self.angleFromSineCosine(sinj2_mm, cosj2_m)

        pairs = [[J1pp, J2pp], [J1pm, J2pm], [J1mp, J2mp], [J1mm, J2mm]]
        index = -1

        j1_min = np.inf
        for i, j in enumerate(pairs):
            if self.checkValidConversion(v, j):
                # This I still need to think about it
                if j[0] < j1_min:
                    index = i
                    j2_min = j[0]
        if index == -1:
            return False, 0, 0, 0
        else:
            return True, pairs[index][0], pairs[index][1]-pairs[index][0], Z

    #Projection of a point into the camera#################################
    def point3DToCameraProjection(self, r):

        ####The distance z of the point has to be that of the plane
        ####This transformation only works when the camera is focused
        ####We invert the Z coordinate
        corrRZ = np.copy(r)
        corrRZ[2] = self.Z0 - r[2]
        corrCameraZ = np.copy(self.camera.r)
        corrCameraZ[2] = self.Z0 - self.camera.r[2]
        
        #print('Punto:', corrRZ)
        #print('R camera:', corrCameraZ)
        s = corrCameraZ - corrRZ
        #print('s:', s)
        #rcdotuz = corrCameraZ[0] * self.camera.uz[0] + corrCameraZ[1] * self.camera.uz[1] + corrCameraZ[2] * self.camera.uz[2]
        sdotuz = s[0]*self.camera.uz[0] + s[1]*self.camera.uz[1] + s[2]*self.camera.uz[2]
        
        l = (self.camera.focaldistance) / sdotuz
        #p = self.camera.r + l * s
        #print('p:', p)
        p = corrCameraZ + l * s
        center = corrCameraZ + self.camera.focaldistance * self.camera.uz
        p = p - center
        #print('ppost:', p) 
        #x = (p[0]*self.camera.ux[0] + p[1]*self.camera.ux[1] + p[2]*self.camera.ux[2])
        #y = (p[0]*self.camera.uy[0] + p[1]*self.camera.uy[1] + p[2]*self.camera.uy[2])
        #print('prex, prey', x, y)
        x = self.camera.cx * (p[0]*self.camera.ux[0] + p[1]*self.camera.ux[1] + p[2]*self.camera.ux[2])
        y = self.camera.cy * (p[0]*self.camera.uy[0] + p[1]*self.camera.uy[1] + p[2]*self.camera.uy[2])
        #print(x)
        #print(y)
        x = x + self.camera.npixelx/2.0
        y = -y + self.camera.npixely/2.0

        return x, y
    
    
    #3D reconstruction point from camera###################################
    def cameraProjectionToPoint3D(self, p_):
       
        p = np.copy(p_)
        corrCameraZ = np.copy(self.camera.r)
        corrCameraZ[2] = self.Z0 - self.camera.r[2]
        
        vx = ((p[0]-self.camera.npixelx/2.0)/self.camera.cx) * self.camera.ux
        vy = ((-p[1]+self.camera.npixely/2.0)/self.camera.cy) * self.camera.uy
        vz = corrCameraZ + self.camera.focaldistance * self.camera.uz

        pointInFocalPlane = vz + vx + vy
        s = corrCameraZ - pointInFocalPlane
        #rcdotuz = corrCameraZ[0] * self.camera.uz[0] + corrCameraZ[1] * self.camera.uz[1] + corrCameraZ[2] * self.camera.uz[2]
        sdotuz = s[0]*self.camera.uz[0] + s[1]*self.camera.uz[1] + s[2]*self.camera.uz[2]
        
        l = (-self.camera.focusdistance) / sdotuz
        #p = self.camera.r + l * s
        p = corrCameraZ + l * s
        return np.asarray([p[0], p[1], self.Z0 - p[2]])

    
  
