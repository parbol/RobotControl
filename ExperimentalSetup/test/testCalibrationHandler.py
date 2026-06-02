from ExperimentalSetup.CalibrationHandler import CalibrationHandler




if __name__ == '__main__':

    cali = CalibrationHandler()
    #cali.writeNewCalibration(cameraX=-1.10303293, cameraY=-95.55517263, c = 256.02657849)
    p = cali.getLastCalibration()
    print(p)


