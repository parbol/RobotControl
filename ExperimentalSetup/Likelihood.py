import numpy as np
import random
import copy

from statsmodels.base.model import GenericLikelihoodModel
from ExperimentalSetup.Robot import Robot
from ExperimentalSetup.Table import Table



class CameraLikelihood(GenericLikelihoodModel):

    def __init__(self, endog, exog, robot, **kwds):
        
        #Input:
        #    endog (array):  reference postions [[X1, Y1, Z1], [X2, Y2, Z2], ...] for each point
        #    exog (array): measurements with the real robot [[J1, J2, J3, J4, X, Y]] 
        
        self.n = int(len(endog))
        self.endog = np.asarray(endog)
        self.exog = np.asarray(exog)
        self.robot = robot
        self.chi2k = []
        super(CameraLikelihood, self).__init__(self.endog, self.exog, self.loglike, **kwds) 


    def loglike(self, params):
        
        # Update camera parameters on each iteration X,Y
        self.robot.camera.r0[0] = params[0]
        self.robot.camera.r0[1] = params[1]
        #self.robot.camera.cy = params[2]
        #self.robot.camera.cx = params[2]
        self.robot.camera.psi = params[2]
        self.robot.camera.update()
        # Compute Log-Like value
        chi2 = 0.0

        for i in range(self.n):

            #Position of the robot
            robotPosition = np.asarray([np.pi / 180.0 * self.exog[i][0], np.pi / 180.0 * self.exog[i][1], self.exog[i][2], np.pi / 180.0 * self.exog[i][3]])
            self.robot.JMoveRobotTo(robotPosition)
            #Nominal position of the point in global coordinates
            nominalPosition = self.endog[i]
            #Nominal position of the point in the camera projection
            xn, yn = self.robot.point3DToCameraProjection(nominalPosition)
            rn = np.asarray([xn, yn])
            #Measurement in the camera system 
            rm = np.asarray([self.exog[i][4], self.exog[i][5]])
            chi2 += np.linalg.norm(rn-rm)**2
        self.chi2k.append(chi2)
        return -chi2


    def check(self):
        
        # Compute Log-Like value
        chi2 = 0.0

        for i in range(self.n):

            #Position of the robot
            robotPosition = np.asarray([np.pi / 180.0 * self.exog[i][0], np.pi / 180.0 * self.exog[i][1], self.exog[i][2], np.pi / 180.0 * self.exog[i][3]])
            self.robot.JMoveRobotTo(robotPosition)
            #Nominal position of the point in global coordinates
            nominalPosition = self.endog[i]
            #Nominal position of the point in the camera projection
            xn, yn = self.robot.point3DToCameraProjection(nominalPosition)
            rn = np.asarray([xn, yn])
            #Measurement in the camera system 
            rm = np.asarray([self.exog[i][4], self.exog[i][5]])
            chi2 += np.linalg.norm(rn-rm)**2
            
            print('------------------------------------------')
            print('Nominal nominalPosition', nominalPosition)
            print('(xn, yn) =', xn, yn)
            print('(xm, ym) =', self.exog[i][4], self.exog[i][5])
            print('Robot position: j1, j2, j3, j4', self.exog[i][0], self.exog[i][1], self.exog[i][2], self.exog[i][3])
            print('Robot position:', self.robot.position)
            print('Parameters:', self.robot.camera.r0[0], self.robot.camera.r0[1], self.robot.camera.cx, self.robot.camera.cy)
            print('------------------------------------------')
            
        
        return chi2


    def fit(self, start_params=None, method='bfgs', maxiter=10000, **kwargs):
        # methods = bfgs, lbfgs, nm, newton, powell, cg, ncg, basinhopping, minimize
        # Only 'powell' method converges and get low chi**2 -> Use POWELL

        if start_params is None:
            # Set initial values for the parameters to optimize
            #start_params = [self.robot.camera.r0[0], self.robot.camera.r0[1], self.robot.camera.cx]
            #start_params = [self.robot.camera.r0[0], self.robot.camera.r0[1], self.robot.camera.cx, -0.5]
            start_params = [self.robot.camera.r0[0], self.robot.camera.r0[1], 1.5]
       
        # Call the parent class's fit method
        return super(CameraLikelihood, self).fit(start_params=start_params, method=method, maxiter=maxiter, **kwargs)
    

