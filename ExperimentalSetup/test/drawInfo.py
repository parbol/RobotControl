import math
import numpy as np
import matplotlib.pyplot as plt
import pickle


def readVals(distanceFile, resultsFile):

    with open(distanceFile, 'r') as fp:
        n = fp.readlines()
    d2 = []
    for d in n:
        d2.append(math.sqrt(float(d)))

    with open(resultsFile, 'rb') as fp:
        t = pickle.load(fp)

    data = []
    for i in t:
        if abs(i[14]-932) <= 20.0:
            data.append(i)

    return d2, data 


#################################################################
def getAllNominalPoints():

    #Here we start from the bottom right 
    firstPointX = -132.0
    firstPointY = -222.0
    px = []
    py = []
    for ix in range(0, 23):
        for iy in range(0, 30):
            px.append(-132.0 + ix * 12.0)
            py.append(-222.0 - iy * 12.0)

    return [px, py]
#################################################################


def extract(data, n):
    
    result = []
    for i in data:
        result.append(i[n])
    return result

if __name__ == "__main__":


    fig, ax = plt.subplots(1,3, figsize = (16, 8))
    distance, data = readVals('output3.txt', 'results.pickle')
    nominal = getAllNominalPoints()
 
    r = extract(data, 14) 
    print('--------------Outlayer analysis----------------')
    badpointsX = []
    badpointsY = []
   
    for i, d in enumerate(data):
        if distance[i] > 0.1:
            print(f'File: {d[10]} has distance: {distance[i]} and radius: {d[14]}, point at ({d[0]},{d[1]})')
            badpointsX.append(d[0])
            badpointsY.append(d[1])
    ax[2].plot(nominal[0], nominal[1], '*')
    ax[2].plot(badpointsX, badpointsY, 'r*')
    print('--------------General statistics----------------')
    print(f'Number of points is: {len(distance)}')
    print(f'Distance is: {np.mean(distance)} +/- {np.std(distance)} with minimum value: {np.min(distance)} and maximum value: {np.max(distance)}')
    print(f'Mean radius is: {np.mean(r)} +/- {np.std(r)} with minimum value: {np.min(r)} and maximum value: {np.max(r)}')
    ax[0].hist(distance, bins=100)
    ax[1].hist(r, bins=100)
  
    plt.show()

