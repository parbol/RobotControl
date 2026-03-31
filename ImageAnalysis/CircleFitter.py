import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize 
from statsmodels.base.model import GenericLikelihoodModel



class CircleFitter(GenericLikelihoodModel):
    """
    Clase Likelihood para crear modelos a partir de los puntos (x, y)
    del borde de un círculo y obtener mediante una minimización la posición
    del centro (x_c, y_c) y el radio r del círculo que mejor se ajusta a los datos.
    """

    def __init__(self, exog, endog, **kwds):
        """
        exog (array):  X, coordenadas x de los puntos del borde del círculo
        endog (array): Y, coordenadas y de los puntos del borde del círculo
        """
        self.n = int(len(exog))
        
        if self.n < 20:
            raise Exception('npoints', 'badnumber')


        self.exog = np.asarray(exog)
        self.endog = np.asarray(endog)
        
        a, b = self.estimateCenter()
        self.a = 400 
        self.b = -200
        self.r = 800

        super(CircleFitter, self).__init__(endog, exog, **kwds)  


    def straightline(self, i, j):

        x1 = self.exog[i]
        y1 = self.endog[i]
        x2 = self.exog[j]
        y2 = self.endog[j]

        mx1 = (x1 + x2) / 2.0
        my1 = (y1 + y2) / 2.0
        vx1 = (x2 - x1)
        vy1 = (y2 - y1)
        ox1 = -vy1
        oy1 = vx1
        o = math.sqrt(ox1**2+oy1**2)
        ox1 = ox1 / o
        oy1 = oy1 / o

        return mx1, my1, ox1, oy1





    def estimateCenter(self):

        p1 = 2
        p2 = int(self.n/2)
        p3 = self.n - 2

        x3 = self.exog[p3]
        y3 = self.endog[p3]





            


    def loglike(self, params):
        #  Se actualizan los parámetros
        self.a = params[0]
        self.b = params[1]
        self.r = params[2]

        chi2 = 0.0

        for i in range(0, self.n):
            chi2 += np.abs(((self.exog[i]-self.a)**2 + (self.endog[i]-self.b)**2 - self.r**2))

        return -chi2

    def fit(self, start_params=None, method='nm', maxiter=10000, **kwargs):

        if start_params is None:
            start_params =  [self.a, self.b, self.r]
        return super(CircleFitter, self).fit(start_params=start_params, method=method, maxiter=maxiter, **kwargs)
    
