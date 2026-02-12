import math
import numpy as np
import matplotlib.pyplot as plt
import sys

from ExperimentalSetup.Table import Table
from ExperimentalSetup.Camera import Camera
from ExperimentalSetup.Robot import Robot

if __name__ == "__main__":

    #Some global variables
    #fig = plt.figure(figsize = plt.figaspect(0.3))
    #fig = plt.figure(figsize = (16, 8), layout="constrained")
    #ax1 = fig.add_subplot(1, 2, 1, projection='3d')
    #ax2 = fig.add_subplot(1, 2, 2)
    #ax1.xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    #ax1.yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    #ax1.zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    #ax1.set_xlabel('x [cm]')
    #ax1.set_ylabel('y [cm]')
    #ax1.set_zlabel('z [cm]')
    #ax1.axes.set_xlim3d(left=-70, right=70.0) 
    #ax1.axes.set_ylim3d(bottom=-70, top=70.0)   
    #ax2.axes.set_xlim((-40.0, 70.0))
    #ax2.axes.set_ylim((-70.0, 40.0))
    #ax2.set_xlabel('x [cm]')
    #ax2.set_ylabel('y [cm]')
    

    fig = plt.figure(figsize = (16, 8), layout="constrained")
    gs0 = fig.add_gridspec(1, 2, width_ratios=[2, 1])
    ax1 = fig.add_subplot(gs0[0], projection = '3d')
    gs1 = gs0[1].subgridspec(2,1)
    ax2 = fig.add_subplot(gs1[0])
    ax3 = fig.add_subplot(gs1[1])
    ax1.xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax1.yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax1.zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax1.set_xlabel('x [cm]')
    ax1.set_ylabel('y [cm]')
    ax1.set_zlabel('z [cm]')
    ax2.set_xlabel('x [cm]')
    ax2.set_ylabel('y [cm]')
    ax3.set_xlabel('z [cm]')
    ax3.set_ylabel('y [cm]')
    ax1.axes.set_xlim3d(left=-70, right=70.0) 
    ax1.axes.set_ylim3d(bottom=-70, top=70.0)   
    ax2.axes.set_xlim((-40.0, 70.0))
    ax2.axes.set_ylim((-70.0, 40.0))
    ax3.axes.set_xlim((-1.0, 1.0))
    ax3.axes.set_ylim((-1.0, 1.0))


    table = Table(0.01, 0.0)
    table.plotTable(ax1, ax2, 'g.')

    # Generate the camera  
    camera = Camera(x = 2.0, y = 0.0, z = -27.0, psi = 0.0, theta = 0.0, phi = 0.0, cx = 0.5, cy = 0.5, focaldistance = 10, sigmaCamera = 0.001)

    # Generate the robot
    robot = Robot(50.0, 30.0, 30.0, 40, table, camera, fig, ax1, ax2, ax3)
    ani = robot.animatedMove(-np.pi/4.0, np.pi + np.pi/4.0, 10.0, 0.0, 200)
    
    plt.show()
