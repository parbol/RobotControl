import math
import numpy as np
import matplotlib.pyplot as plt
import sys

from ExperimentalSetup.Table import Table

if __name__ == "__main__":

    #Some global variables
    #fig = plt.figure(figsize = plt.figaspect(0.3))
    fig = plt.figure(figsize = (16, 8), layout="constrained")
    ax1 = fig.add_subplot(1, 2, 1, projection='3d')
    ax2 = fig.add_subplot(1, 2, 2)
    ax1.xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax1.yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax1.zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax1.set_xlabel('x [cm]')
    ax1.set_ylabel('y [cm]')
    ax1.set_zlabel('z [cm]')
    ax1.axes.set_xlim3d(left=-70, right=70.0) 
    ax1.axes.set_ylim3d(bottom=-70, top=70.0)   
    ax2.axes.set_xlim((-40.0, 70.0))
    ax2.axes.set_ylim((-70.0, 40.0))
    ax2.set_xlabel('x [cm]')
    ax2.set_ylabel('y [cm]')
    
    table = Table(0.01, 0.0)
    table.generatePoints()
    table.plotTable(ax1, ax2, 'g.')
    plt.show()
