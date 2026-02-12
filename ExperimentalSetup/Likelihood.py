from statsmodels.base.model import GenericLikelihoodModel
import numpy as np
import matplotlib.pyplot as plt

from src.Robot import Robot

class MyLikelihood(GenericLikelihoodModel):

   def __init__(self, endog, exog, robot, **kwds):

      self.n = int(len(endog)/3)
      rPoints_ = np.copy(endog)
      self.rPoints = np.asmatrix(rPoints_.reshape(self.n, 3))
      cPoints_ = np.copy(exog)
      self.cPoints = np.asmatrix(cPoints_.reshape(self.n, 3))
      self.robot = robot
      self.sigma2 = self.robot.sigmaCamera**2 + self.robot.sigmaRobot**2
      super(MyLikelihood, self).__init__(endog, exog, **kwds)


   def loglike(self, params):

      self.robot.param[0] = params[0]
      self.robot.param[1] = params[1]
      chi2 = 0.0
      for i in range(0, self.n):
         rPoint = np.asarray([self.rPoints[i, 0], self.rPoints[i, 1], self.rPoints[i, 2]])
         cPoint = np.asarray([self.cPoints[i, 0], self.cPoints[i, 1], self.cPoints[i, 2]])
         valid, cPointGlobal = self.robot.fromCameraToGlobalSystem(rPoint, cPoint)
         chi2 += ((rPoint[0]-cPointGlobal[0])**2 + (rPoint[1]-cPointGlobal[1])**2)/self.sigma2
      return -chi2
   
     