"""
Euler Rotation class, to orientate objects.
R(psi, theta, phi)
Applied as:
    phi -> Rotation on z axis
    theta -> Rotation on x axis
    psi -> Rotation on z axis
"""

import numpy as np
import random
import sys

class EulerRotation():

    def __init__(self, psi = 0.0, theta = 0.0, phi = 0.0):
        
        self.psi = psi
        self.theta = theta
        self.phi = phi
        self.rot = self.makeMatrix(self.psi, self.theta, self.phi)
        # print(self.rot)
        self.vx, self.vy, self.vz = self.fromMatrixToVectors(self.rot)
        self.invrot = np.linalg.inv(self.rot)

    def setFromAngles(self, psi, theta, phi):
        self.psi = psi
        self.theta = theta
        self.phi = phi
        self.rot = self.makeMatrix(self.psi, self.theta, self.phi)
        self.vx, self.vy, self.vz = self.fromMatrixToVectors(self.rot)
        self.invrot = np.linalg.inv(self.rot)

    def setFromVectors(self, vx, vy, vz):
        
        self.rot = self.makeMatrixFromVector(vx, vy, vz)
        self.vx = vx
        self.vy = vy
        self.vz = vz
        self.psi, self.theta, self.phi = self.fromMatrixToAngle(self.rot)
        self.invrot = np.linalg.inv(self.rot)

    def fromMatrixToVectors(self, A):

        vx = np.asarray([A[0,0], A[1,0], A[2,0]])
        vy = np.asarray([A[0,1], A[1,1], A[2,1]])
        vz = np.asarray([A[0,2], A[1,2], A[2,2]])

        return vx, vy, vz


    def makeMatrix(self, psi, theta, phi):

        B_ = [[np.cos(psi), np.sin(psi), 0.0],
              [-np.sin(psi), np.cos(psi), 0.0],
              [0.0, 0.0, 1.0]]
        B = np.asmatrix(B_)

        D_ = [[np.cos(phi), np.sin(phi), 0.0],
              [-np.sin(phi), np.cos(phi), 0.0],
              [0.0, 0.0, 1.0]]
        D = np.asmatrix(D_)

        C_ = [[1.0, 0, 0],
              [0.0, np.cos(theta), np.sin(theta)],
              [0.0, -np.sin(theta), np.cos(theta)]]
        C = np.asmatrix(C_)

        return B.dot(C.dot(D))



    def makeMatrixFromVector(self, vx, vy, vz):

        A_ = [[vx[0], vy[0], vz[0]],
              [vx[1], vy[1], vz[1]],
              [vx[2], vy[2], vz[2]]]
        A = np.asmatrix(A_)

        return A


    def makePositive(self, angle):

        theAngle = angle
        # while theAngle > 0:
        #     theAngle = theAngle - 2.0 * np.pi    

        while theAngle < 0:
            theAngle = theAngle + 2.0 * np.pi
        
        return theAngle


    def apply(self, v):

        return np.asarray(self.rot.dot(v))[0]
    

    def applyInverse(self, v):

        return np.asarray(self.invrot.dot(v))[0]
    

    def fromMatrixToAngle(self, A):

        theta = np.arccos(A[2,2])
        if np.sin(theta) > 1e-7:
            sinphi = A[2,0]/np.sin(theta)
            cosphi = -A[2,1]/np.sin(theta)
            if sinphi >= 0:
                phi = np.arccos(cosphi)
            else:
                phi = -np.arccos(cosphi)
            sinpsi = A[0,2]/np.sin(theta)
            cospsi = A[1,2]/np.sin(theta)
            if sinpsi >= 0:
                psi = np.arccos(cospsi)
            else:
                psi = -np.arccos(cospsi)
        else:
            if np.cos(theta) >= 0:
                if A[0,1] > 0:
                    psi = np.arccos(A[0,0])
                    theta = 0.0
                    phi = 0.0
                else:
                    psi = -np.arccos(A[0,0])
                    theta = 0.0
                    phi = 0.0   
            else:
                if A[0,1] > 0:
                    psi = -np.arccos(A[0,0])
                    theta = np.pi
                    phi = 0.0   
                else:
                    psi = np.arccos(A[0,0])
                    theta = np.pi
                    phi = 0.0   
        psi = self.makePositive(psi)
        theta = self.makePositive(theta)
        phi = self.makePositive(phi)
        return psi, theta, phi 




def test_Euler():
    """
    Short script to Test if the matrix problem is solved correcty.
    Los angulos no son unívocos: siempre hay dos soluciones posibles, y en theta = 0, el sistema esta 
    degenerado con infinitas soluciones

    -De una matriz hay dos soluciones de (psi,theta,phi), arccos(theta) =  arccos(theta+pi)
    -Gimball Lock cuando theta = 0 
    -De dos sets de ángulos distintos (theta) y (theta + pi), obtengo la misma matriz -> ¿DEgeneración?
    """
    lim = np.pi 
    lim = 0.2
    psi = random.uniform(-lim, lim) 
    theta = random.uniform(-lim, lim) 
    phi = random.uniform(-lim, lim) 

    rotacion = EulerRotation(psi, theta, phi)
    transform = rotacion.fromMatrixToAngle(rotacion.rot)

    psi, theta, phi = rotacion.makePositive(psi), rotacion.makePositive(theta), rotacion.makePositive(phi)

    print('Test Euler Angles')
    print('psi \t theta\t phi')
    print(f'{psi:.3f} \t {theta:.3f} \t {phi:.3f}')
    print(f'{transform[0]:.3f} \t {transform[1]:.3f} \t {transform[2]:.3f}')
    print(f'{(transform[0]-psi)<1e-4} \t {(transform[1]-theta)<1e-4} \t {(transform[2]-phi)<1e-4}')

    print(rotacion.rot)
    print(EulerRotation(transform[0],transform[1],transform[2]).rot)
    print((EulerRotation(transform[0],transform[1],transform[2]).rot - rotacion.rot )<10e-5)


if __name__ =='__main__':
    test_Euler()
