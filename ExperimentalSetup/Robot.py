import numpy as np
import sys
import math as math
from matplotlib.animation import FuncAnimation, writers
from src.Camera import Camera
from src.EulerRotation import EulerRotation
from src.Table import Table

####################################################################
# Some definitions                                                 #
# The robot pointer has two systems of coordinates:                #
# Cartesian: (x, y, z) and JZ = position of the pointer and JZ     #
# Inner: (J1, J2, Z) and JZ = rotations of the axis                #
# The robot pointer position z is Z0 - Z                           #
####################################################################
# The robot has also two systems of reference:                     #
# The absolute one (x, y, z)                                       # 
# And the one of the second leg focused at the pointer             #
####################################################################


class Robot:

    def __init__(self, h, R1, R2, Z0, table, camera, fig, ax1, ax2, ax3):

        #Robot parameters
        self.h = h
        self.R1 = R1
        self.R2 = R2
        #Z0 is the height of the pointer of the robot when Z = 0
        self.Z0 = Z0
        self.tol = 1e-8
        #Camera and table
        self.camera = camera
        self.table = table
        #Current position
        self.J1 = 0.0
        self.J2 = 0.0
        self.Z = 0.0
        self.J1s = 0.0
        self.J2s = 0.0
        self.Zs = 0.0
        self.J1e = 0.0
        self.J2e = 0.0
        self.Ze = 0.0
        self.Jz = 0.0
        self.r = np.asarray([0.0, 0.0, 0.0])
        self.ux = np.asarray([1.0, 0.0, 0.0])
        self.uz = np.asarray([0.0, 1.0, 0.0])
        self.uy = np.asarray([0.0, 0.0, 1.0])
        self.frame = [np.asarray([0.0, 0.0, 0.0]), np.asarray([0.0, 0.0, 0.0]), np.asarray([0.0, 0.0, 0.0]), np.asarray([0.0, 0.0, 0.0])]
        self.N = 0
        self.fig = fig
        self.ax1 = ax1
        self.ax2 = ax2
        self.ax3 = ax3
        self.innerMoveTo(self.J1, self.J2, self.Z, self.Jz)



    ######### Set camera globals #######################################
    def updateCameraGlobals(self):
        
        self.camera.r0global = np.asarray([self.r[0], self.r[1], 0.0]) + self.camera.r0[0] * self.ux + self.camera.r0[1] * self.uy + (self.h + self.camera.r0[2]) * self.uz
        self.camera.uxglobal = self.camera.rotation0.apply(self.ux)
        self.camera.uyglobal = self.camera.rotation0.apply(self.uy)
        self.camera.uzglobal = self.camera.rotation0.apply(self.uz)
        p1 = [1.0, 1.0]
        p2 = [1.0, -1.0]
        p3 = [-1.0, -1.0]
        p4 = [-1.0, 1.0]
        self.frame[0] = self.cameraProjectionToPoint3D(p1)
        self.frame[1] = self.cameraProjectionToPoint3D(p2)
        self.frame[2] = self.cameraProjectionToPoint3D(p3)
        self.frame[3] = self.cameraProjectionToPoint3D(p4)

       
    def checkInFrame(self, p):
        
        x, y = self.point3DToCameraProjection(p)
        if x >= -1.0 and x <= 1.0 and y >= -1.0 and y <= 1.0:
            return True
        return False

    ######### Move the robot ###########################################
    def innerMoveTo(self, j1, j2, z, jz):
        self.J1 = j1
        self.J2 = j2
        self.Z = z
        self.Jz = jz
        self.r = self.fromInnerToCartesian(self.J1, self.J2, self.Z)
        self.ux = np.asarray([np.cos(self.J1+self.J2), np.sin(self.J1+self.J2), 0.0])
        self.uy = np.asarray([-np.sin(self.J1+self.J2), np.cos(self.J1+self.J2), 0.0])
        self.uz = np.asarray([0.0, 0.0, 1.0])
        self.updateCameraGlobals()

    ########## Animated function ########################################
    def animation_function(self, i):
    
        a = math.floor(self.N/3.0)
        b = math.floor(2.0*self.N/3.0)
        j1 = 0
        j2 = 0
        z = 0
        if i <= a:
            j1 = self.J1s + i * (self.J1e - self.J1s) / a
            j2 = self.J2s
            z = self.Zs
            self.innerMoveTo(j1, j2, z, 0.0)
            self.drawRobot(self.ax1, self.ax2, self.ax3, 'y')
        elif i > a and i <= b:
            k = i - a - 1
            j1 = self.J1e
            j2 = self.J2s + k * (self.J2e - self.J2s) / (b-a-1)
            z = self.Zs 
            self.innerMoveTo(j1, j2, z, 0.0)
            self.drawRobot(self.ax1, self.ax2, self.ax3, 'y')
        else:
            k = i - b - 1
            j1 = self.J1e
            j2 = self.J2e
            z = self.Zs + k * (self.Ze - self.Zs) / (self.N - 1 - b - 1)
            self.innerMoveTo(j1, j2, z, 0.0)
            self.drawRobot(self.ax1, self.ax2, self.ax3, 'y')

    ########## Animated move ########################################
    def animatedMove(self, j1, j2, z, jz, N):
    
        self.J1s = self.J1
        self.J2s = self.J2
        self.Zs = self.Z
        self.J1e = j1
        self.J2e = j2
        self.Ze = z
        self.N = N
        ani = FuncAnimation(self.fig, self.animation_function, frames=self.N, interval=1, blit=True)
        return ani


    ######### Move the robot ###########################################
    def cartesianMoveTo(self, v, jz):
        self.r = v
        self.Jz = jz
        status, j1, j2, Z = self.fromCartesianToInner(v)
        if status:
            self.J1 = j1
            self.J2 = j2
            self.Z = Z
            self.ux = np.asarray([np.cos(self.J1+self.J2), np.sin(self.J1+self.J2), 0.0])
            self.uy = np.asarray([-np.sin(self.J1+self.J2), np.cos(self.J1+self.J2), 0.0])
            self.uz = np.asarray([0.0, 0.0, 1.0])
            self.updateCameraGlobals()
        else:
            print('There was an error moving the robot')
            sys.exit()     

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
        if (x-v[0])**2 + (y-v[1])**2 < 1e-5:
            return True
        return False
    
    ######################################################################
    def fromInnerToCartesian(self, J1, J2, Z):

        x = self.R1 * np.cos(J1) + self.R2 * np.cos(J2+J1)
        y = self.R1 * np.sin(J1) + self.R2 * np.sin(J2+J1)
        z = self.Z0 - Z
        return np.asarray([x, y, z])
    
    ######################################################################
    def fromCartesianToInner(self, v):

        x = v[0]
        y = v[1]
        z = v[2]
        Z = self.Z0 - z
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
        j1 = 1000.0
        for i, j in enumerate(pairs):
            if self.checkValidConversion(v, j):
                if j[0] >= 0 and j[0] < j1:
                    index = i
                    j1 = j[0]
        if index == -1:
            return False, 0, 0, 0
        else:
            return True, pairs[index][0], pairs[index][1]-pairs[index][0], Z

    #Projection of a point into the camera
    def point3DToCameraProjection(self, r):

        s = self.camera.r0global - r
        l = self.camera.focaldistance / (s[0]*self.camera.uzglobal[0] + s[1]*self.camera.uzglobal[1] + s[2]*self.camera.uzglobal[2])
        p = self.camera.r0global + l * (self.camera.r0global - r)
        center = self.camera.r0global + self.camera.focaldistance * self.camera.uzglobal
        p = p - center

        x = self.camera.cx * (p[0]*self.camera.uxglobal[0] + p[1]*self.camera.uxglobal[1] + p[2]*self.camera.uxglobal[2])
        y = self.camera.cy * (p[0]*self.camera.uyglobal[0] + p[1]*self.camera.uyglobal[1] + p[2]*self.camera.uyglobal[2])
        return x, y
    
    #3D reconstruction point from camera
    def cameraProjectionToPoint3D(self, p):
        x = p[0]/self.camera.cx
        y = p[1]/self.camera.cy
        center = self.camera.r0global + self.camera.focaldistance * self.camera.uzglobal

        t = x * self.camera.uxglobal + y * self.camera.uyglobal + center
        s = self.camera.r0global - t
        
        l = (self.table.z-self.camera.r0global[2])/s[2]
        point3D = self.camera.r0global + l * s
        return point3D

    # Drawing the robot
    def drawRobot(self, ax1, ax2, ax3, t, alpha=1.0):
    
        ax1.clear()
        ax2.clear()
        ax3.clear()
        ax1.axes.set_xlim3d(left=-70, right=70.0) 
        ax1.axes.set_ylim3d(bottom=-70, top=70.0)   
        ax2.axes.set_xlim((-40.0, 70.0))
        ax2.axes.set_ylim((-70.0, 40.0))
        ax3.axes.set_xlim((-1.0, 1.0))
        ax3.axes.set_ylim((-1.0, 1.0))
        self.table.plotTable(ax1, ax2, 'g.')
        p1 = [0, 0, 0]
        p2 = [0, 0, self.h]
        p3 = [self.R1 * np.cos(self.J1), self.R1 * np.sin(self.J1), self.h]
        p4 = [p3[0] + self.R2 * np.cos(self.J1+self.J2), p3[1] + self.R2 * np.sin(self.J1+self.J2), self.h]
        p5 = [p4[0], p4[1], self.Z0]
        p6 = [p4[0], p4[1], self.r[2]]
        x_start = [p1[0], p2[0], p3[0], p4[0], p5[0]]
        y_start = [p1[1], p2[1], p3[1], p4[1], p5[1]]
        z_start = [p1[2], p2[2], p3[2], p4[2], p5[2]]
        x_start2 = [p5[0], p6[0]]
        y_start2 = [p5[1], p6[1]]
        z_start2 = [p5[2], p6[2]]
               
        p7 = np.asarray([self.camera.r0global[0], self.camera.r0global[1], self.h])
        p8 = self.camera.r0global
        x_start3 = [p4[0], p7[0], p8[0]]
        y_start3 = [p4[1], p7[1], p8[1]]
        z_start3 = [p4[2], p7[2], p8[2]]

        k1 = [1.0, 1.0]
        k2 = [1.0, -1.0]
        k3 = [-1.0, -1.0]
        k4 = [-1.0, 1.0]
        k1p = self.cameraProjectionToPoint3D(k1)
        k2p = self.cameraProjectionToPoint3D(k2)
        k3p = self.cameraProjectionToPoint3D(k3)
        k4p = self.cameraProjectionToPoint3D(k4)

        k1p = self.frame[0]
        k2p = self.frame[1]
        k3p = self.frame[2]
        k4p = self.frame[3]

        x_start4 = [p8[0], k1p[0]]
        y_start4 = [p8[1], k1p[1]]
        z_start4 = [p8[2], k1p[2]]
        x_start5 = [p8[0], k2p[0]]
        y_start5 = [p8[1], k2p[1]]
        z_start5 = [p8[2], k2p[2]]
        x_start6 = [p8[0], k3p[0]]
        y_start6 = [p8[1], k3p[1]]
        z_start6 = [p8[2], k3p[2]]
        x_start7 = [p8[0], k4p[0]]
        y_start7 = [p8[1], k4p[1]]
        z_start7 = [p8[2], k4p[2]]
        x_start8 = [k1p[0], k2p[0], k3p[0], k4p[0], k1p[0]]
        y_start8 = [k1p[1], k2p[1], k3p[1], k4p[1], k1p[1]]
        z_start8 = [k1p[2], k2p[2], k3p[2], k4p[2], k1p[2]]

        ax1.plot3D(x_start , y_start, z_start, t, alpha=alpha)
        ax1.plot3D(x_start2 , y_start2, z_start2, 'r', alpha=alpha)
        ax1.plot3D(x_start3 , y_start3, z_start3, 'g', alpha=alpha)
        ax1.plot3D(x_start4 , y_start4, z_start4, 'k', alpha=alpha)
        ax1.plot3D(x_start5 , y_start5, z_start5, 'k', alpha=alpha)
        ax1.plot3D(x_start6 , y_start6, z_start6, 'k', alpha=alpha)
        ax1.plot3D(x_start7 , y_start7, z_start7, 'k', alpha=alpha)
        ax1.plot3D(x_start8 , y_start8, z_start8, 'k', alpha=alpha)

        ax2.plot(x_start, y_start, t, alpha=alpha)
        ax2.plot(x_start3, y_start3, 'g', alpha=alpha)
        ax2.plot(x_start8, y_start8, 'k', alpha=alpha)
        for p in self.table.actualPoints:
            if self.checkInFrame(p):
                x, y = self.point3DToCameraProjection(p)
                ax3.plot(x, y, 'b*', alpha=alpha)

