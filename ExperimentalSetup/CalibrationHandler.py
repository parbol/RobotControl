from datetime import datetime


class CalibrationHandler:

    def __init__(self, name='../../ExperimentalSetup/Calibrations/calibrations.txt'):

        self.name = name
        f = open(self.name)
        self.calibrations = f.readlines()
        self.N = len(self.calibrations)
        f.close()


    ########################################################################
    def parseTextToCalibration(self, line_):

        line = line_.split()
        cali = dict()
        cali['N'] = int(line[1])
        cali['date'] = line[3]
        cali['R1'] = float(line[5])
        cali['R2'] = float(line[7])
        cali['Z0'] = float(line[9])
        cali['focaldistance'] = float(line[11])
        cali['focusdistance'] = float(line[13])
        cali['cameraX'] = float(line[15])
        cali['cameraY'] = float(line[17])
        cali['cameraZ'] = float(line[19])
        cali['cameraPsi'] = float(line[21])
        cali['cameraTheta'] = float(line[23])
        cali['cameraPhi'] = float(line[25])
        cali['c'] = float(line[27])
        return cali


    ##################################################################   
    def parseCalibrationToText(self, cali):
        
        line = ''
        for j, key in enumerate(cali):
            if j == 0:
                line = line + key + ' ' + str(cali[key])
            else:
                line = line + ' ' + key + ' ' + str(cali[key])
        return line

    ##################################################################   
    def getCalibration(self, N):

        for cal in self.calibrations:
            cali = self.parseTextToCalibration(cal)
            if cali['N'] == N:
                return cali


    ##################################################################   
    def getLastCalibration(self):

        cal = self.calibrations[len(self.calibrations)-1]
        cali = self.parseTextToCalibration(cal)
        return cali


    ##################################################################   
    def writeNewCalibration(self, R1 = 380, R2 = 240, Z0 = 400, 
                            focaldistance = 200, focusdistance = 36,
                            cameraX = 0, cameraY = 0, cameraZ = 0,
                            cameraPsi = 0, cameraTheta = 0, 
                            cameraPhi = 0, c = 256):
        
        
        print('-----------------------')
        cali = dict()
        cali['N'] = self.N
        cali['date'] = datetime.today().isoformat()
        cali['R1'] = R1
        cali['R2'] = R2
        cali['Z0'] = Z0
        cali['focaldistance'] = focaldistance
        cali['focusdistance'] = focusdistance
        cali['cameraX'] = cameraX
        cali['cameraY'] = cameraY
        cali['cameraZ'] = cameraZ
        cali['cameraPsi'] =  cameraPsi
        cali['cameraTheta'] = cameraTheta
        cali['cameraPhi'] = cameraPhi
        cali['c'] = c

        self.N = self.N + 1
        line = self.parseCalibrationToText(cali)
        print(line)
        f = open(self.name, 'a')
        f.write(line + '\n')
        f.close()



