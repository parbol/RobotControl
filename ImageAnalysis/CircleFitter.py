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
        
        self.exog = np.asarray(exog)
        self.endog = np.asarray(endog)
        self.a = 400 
        self.b = -200
        self.r = (np.max([(max(self.exog)-min(self.exog)), (max(self.endog)-min(self.endog))]))

        super(CircleFitter, self).__init__(endog, exog, **kwds)  

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
    
