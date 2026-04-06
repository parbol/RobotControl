import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize 
from statsmodels.base.model import GenericLikelihoodModel
import math


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
        self.a = a 
        self.b = -b
        self.r = 800
        super(CircleFitter, self).__init__(endog, exog, **kwds)  

    def straightLine(self, i, j):

        x1 = self.exog[i]
        y1 = self.endog[i]
        x2 = self.exog[j]
        y2 = self.endog[j]
        if x1 == x2 and y1 == y2:
            return 0,0,0,0, False
        mx1 = (x1 + x2) / 2.0
        my1 = (y1 + y2) / 2.0
        vx1 = (x2 - x1)
        vy1 = (y2 - y1)
        ox1 = -vy1
        oy1 = vx1
        o = math.sqrt(ox1**2+oy1**2)
        ox1 = ox1 / o
        oy1 = oy1 / o

        return mx1, my1, ox1, oy1, True

    def centerTwoLines(self, i, j, k, l):

        mx1, my1, ox1, oy1, valid1 = self.straightLine(i, j)
        mx2, my2, ox2, oy2, valid2 = self.straightLine(k, l)
        if not valid1 or not valid2:
            return 0, 0, False
        if abs(oy2) < 1e-6:
            l = (my2-my1)/oy1
        else:
            if abs((ox1 - oy1/oy2 * ox2)) < 1e-6:
                return 0, 0, False
            l = ((mx2 - mx1) - ox2/oy2 * (my2 - my1)) / (ox1 - oy1/oy2 * ox2)
        x = mx1 + l * ox1
        y = my1 + l * oy1
        return x, y, True 

    def estimateCenter(self):

        p1 = 2
        p2 = int(self.n/3)
        p3 = int(2.0*self.n/3)
        p4 = self.n - 2
        centers = []
        p = [[p1, p2], [p1, p3], [p1, p4], [p2, p3], [p2, p4], [p3, p4]]
        xc = 0
        yc = 0
        n = 0
        for i, pi in enumerate(p):
            for j, pj in enumerate(p):
                if i == j:
                    continue
                x, y, valid = self.centerTwoLines(p[i][0], p[i][1], p[j][0], p[j][1])
                if not valid:
                    continue
                centers.append([x, y])
                xc = xc + x
                yc = yc + y
                n = n + 1
        
        return xc / n, yc / n 

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
        print('Starting fitting.....')
        if start_params is None:
            start_params =  [self.a, self.b, self.r]
        return super(CircleFitter, self).fit(start_params=start_params, method=method, maxiter=maxiter, **kwargs)
    
