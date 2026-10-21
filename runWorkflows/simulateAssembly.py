import numpy as np
import matplotlib.pyplot as plt


###################################################################################################
###################################################################################################
######################################## Constants ################################################
nominalCorner0ETROC = np.asarray([-23.0/2.0, 21.0/2.0])
nominalCorner1ETROC = np.asarray([-23.0/2.0, -21.0/2.0])
nominalCorner2ETROC = np.asarray([23.0/2.0, 21.0/2.0])
nominalCorner3ETROC = np.asarray([23.0/2.0, -21.0/2.0]) 
nominalCornersETROC = np.array([nominalCorner0ETROC, nominalCorner1ETROC, nominalCorner2ETROC, nominalCorner3ETROC])
ETROCCenterShift = np.asarray([-23.0/2.0, 21.0/2.0])
nominalFiducial0ETROC = np.asarray([2.50, -1.0]) + ETROCCenterShift
nominalFiducial1ETROC = np.asarray([2.50, -20.0]) + ETROCCenterShift
nominalFiducial2ETROC = np.asarray([22.0, -1.0]) + ETROCCenterShift
nominalFiducial3ETROC = np.asarray([22.0, -20.0]) + ETROCCenterShift
nominalFiducialsETROC = np.array([nominalFiducial0ETROC, nominalFiducial1ETROC, nominalFiducial2ETROC, nominalFiducial3ETROC])
ETROCPositionInChuckA = np.asarray([-100.0, 500.0])
ETROCPositionInChuckB = np.asarray([-150.0, 500.0])
ETROCPositionInChuckC = np.asarray([-200.0, 500.0])
ETROCPositionInChuckD = np.asarray([-250.0, 500.0])
ETROCPositionsInChuck = np.array([ETROCPositionInChuckA, ETROCPositionInChuckB, ETROCPositionInChuckC, ETROCPositionInChuckD])
nominalCorner0PCB = np.asarray([-57.5/2.0, 44.1/2.0])
nominalCorner1PCB = np.asarray([-57.5/2.0, -44.1/2.0])
nominalCorner2PCB = np.asarray([57.5/2.0, 44.1/2.0])
nominalCorner3PCB = np.asarray([57.5/2.0, -44.1/2.0])
nominalCornersPCB = np.array([nominalCorner0PCB, nominalCorner1PCB, nominalCorner2PCB, nominalCorner3PCB])
PCBCenterShift = np.asarray([-57.5/2.0, 44.1/2.0])
nominalFiducial0PCB = np.asarray([2.0, -2.5]) + PCBCenterShift
nominalFiducial1PCB = np.asarray([2.0, -41.6]) + PCBCenterShift
nominalFiducial2PCB = np.asarray([55.5, -2.5]) + PCBCenterShift
nominalFiducial3PCB = np.asarray([55.5, -41.6]) + PCBCenterShift
nominalFiducialsPCB = np.array([nominalFiducial0PCB, nominalFiducial1PCB, nominalFiducial2PCB, nominalFiducial3PCB])
PCBPositionInChuck = np.asarray([-100.0, 425.0])
etroc_gap = 0.2
ETROCPositionInPCBA = nominalCorner0ETROC + np.asarray([-etroc_gap/2.0, etroc_gap/2.0])
ETROCPositionInPCBB = nominalCorner1ETROC + np.asarray([-etroc_gap/2.0, -etroc_gap/2.0])
ETROCPositionInPCBC = nominalCorner2ETROC + np.asarray([etroc_gap/2.0, etroc_gap/2.0])
ETROCPositionInPCBD = nominalCorner3ETROC + np.asarray([etroc_gap/2.0, -etroc_gap/2.0])
ETROCPositionsInPCB = np.array([ETROCPositionInPCBA, ETROCPositionInPCBB, ETROCPositionInPCBC, ETROCPositionInPCBD])
###################################################################################################
mm = 1.0
ETROC_CENTER_CORRECTION = [0.00*mm, 0.00*mm]
ETROC_SIZE = [23*mm, 21*mm]
ETROC_GAP = 0.2*mm
# CORRECTION = [0*mm, -0.5*mm]
CORRECTION = [0*mm, 0*mm]
###################################################################################################
###################################################################################################
###################################################################################################




class ETROC:

    def __init__(self, corners, fiducialMarks):
        
        self.nomCorners = corners
        self.nomFiducialMarks = fiducialMarks
        self.nomCenter = np.asarray([0.0, 0.0])
        for c in self.nomCorners:
            self.nomCenter += c
        self.nomCenter /= len(self.nomCorners)
        
        self.corners = np.array([np.asarray([0.0, 0.0]) for i in range(len(corners))])
        self.fiducialMarks = np.array([np.asarray([0.0, 0.0]) for i in range(len(fiducialMarks))])
        self.center = np.asarray([0.0, 0.0])
        self.finalCorners = np.array([np.asarray([0.0, 0.0]) for i in range(len(corners))])
        self.finalFiducialMarks = np.array([np.asarray([0.0, 0.0]) for i in range(len(fiducialMarks))])
        self.finalCenter = np.asarray([0.0, 0.0])

    def move(self, p, theta):

        rotation = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
        for i, c in enumerate(self.nomCorners):     
            self.corners[i] = p + rotation @ c
        for i, f in enumerate(self.nomFiducialMarks):
            self.fiducialMarks[i] = p + rotation @ f
        self.center = p + rotation @ self.nomCenter


    def updatePosition(self, grabPoint, fakeTheta, finalPoint):

        rotation = np.array([[np.cos(fakeTheta), -np.sin(fakeTheta)], [np.sin(fakeTheta), np.cos(fakeTheta)]])
        for i, f in enumerate(self.corners):
            pos = f - grabPoint
            newpos = rotation @ pos
            finalpos = finalPoint + newpos
            self.finalCorners[i] = finalpos
            self.finalCenter = self.finalCenter + finalpos
        self.finalCenter /= len(self.finalCorners)
        for i, f in enumerate(self.fiducialMarks):
            pos = f - grabPoint
            newpos = rotation @ pos
            finalpos = finalPoint + newpos
            self.finalFiducialMarks[i] = finalpos
            
            
    def draw(self, ax):
        # Draw ETROC
        ax[0].plot([self.corners[0][0], self.corners[1][0]], [self.corners[0][1], self.corners[1][1]], 'b-')
        ax[0].plot([self.corners[1][0], self.corners[3][0]], [self.corners[1][1], self.corners[3][1]], 'b-')
        ax[0].plot([self.corners[3][0], self.corners[2][0]], [self.corners[3][1], self.corners[2][1]], 'b-')
        ax[0].plot([self.corners[2][0], self.corners[0][0]], [self.corners[2][1], self.corners[0][1]], 'b-')
        # Draw fiducial marks
        ax[1].plot(self.fiducialMarks[:, 0], self.fiducialMarks[:, 1], 'ro')
        # Draw center
        ax[0].plot(self.center[0], self.center[1], 'kx')

        # Draw ETROC
        ax[1].plot([self.finalCorners[0][0], self.finalCorners[1][0]], [self.finalCorners[0][1], self.finalCorners[1][1]], 'b-')
        ax[1].plot([self.finalCorners[1][0], self.finalCorners[3][0]], [self.finalCorners[1][1], self.finalCorners[3][1]], 'b-')
        ax[1].plot([self.finalCorners[3][0], self.finalCorners[2][0]], [self.finalCorners[3][1], self.finalCorners[2][1]], 'b-')
        ax[1].plot([self.finalCorners[2][0], self.finalCorners[0][0]], [self.finalCorners[2][1], self.finalCorners[0][1]], 'b-')
        # Draw fiducial marks
        ax[1].plot(self.finalFiducialMarks[:, 0], self.finalFiducialMarks[:, 1], 'ro')
        # Draw center
        ax[1].plot(self.finalCenter[0], self.finalCenter[1], 'kx')



class PCB:

    def __init__(self, corners, fiducialMarks, etrocPositions):
        
        self.nomCorners = corners
        self.nomFiducialMarks = fiducialMarks
        self.nomCenter = np.asarray([0.0, 0.0])
        self.nomEtrocPositions = etrocPositions
        for c in self.nomCorners:
            self.nomCenter += c
        self.nomCenter /= len(self.nomCorners)
        
        self.corners = np.array([np.asarray([0.0, 0.0]) for i in range(len(corners))])
        self.fiducialMarks = np.array([np.asarray([0.0, 0.0]) for i in range(len(fiducialMarks))])
        self.center = np.asarray([0.0, 0.0])
        self.etrocPositions = np.array([np.asarray([0.0, 0.0]) for i in range(len(etrocPositions))])


    def move(self, p, theta):

        rotation = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
        for i, c in enumerate(self.nomCorners):
            self.corners[i] = p + rotation @ c
        for i, f in enumerate(self.nomFiducialMarks):
            self.fiducialMarks[i] = p + rotation @ f
        for i, e in enumerate(self.nomEtrocPositions):
            self.etrocPositions[i] = p + rotation @ e
        self.center = p + rotation @ self.nomCenter


    def draw(self, ax):
        # Draw PCB
        ax[0].plot([self.corners[0][0], self.corners[1][0]], [self.corners[0][1], self.corners[1][1]], 'b-')
        ax[0].plot([self.corners[1][0], self.corners[3][0]], [self.corners[1][1], self.corners[3][1]], 'b-')
        ax[0].plot([self.corners[3][0], self.corners[2][0]], [self.corners[3][1], self.corners[2][1]], 'b-')
        ax[0].plot([self.corners[2][0], self.corners[0][0]], [self.corners[2][1], self.corners[0][1]], 'b-')
        # Draw fiducial marks
        ax[0].plot(self.fiducialMarks[:, 0], self.fiducialMarks[:, 1], 'ro')
        # Draw ETROC positions
        ax[0].plot(self.etrocPositions[:, 0], self.etrocPositions[:, 1], 'g+')
        # Draw center
        ax[0].plot(self.center[0], self.center[1], 'kx')

        ax[1].plot([self.corners[0][0], self.corners[1][0]], [self.corners[0][1], self.corners[1][1]], 'b-')
        ax[1].plot([self.corners[1][0], self.corners[3][0]], [self.corners[1][1], self.corners[3][1]], 'b-')
        ax[1].plot([self.corners[3][0], self.corners[2][0]], [self.corners[3][1], self.corners[2][1]], 'b-')
        ax[1].plot([self.corners[2][0], self.corners[0][0]], [self.corners[2][1], self.corners[0][1]], 'b-')
        # Draw fiducial marks
        ax[1].plot(self.fiducialMarks[:, 0], self.fiducialMarks[:, 1], 'ro')
        # Draw ETROC positions
        ax[1].plot(self.etrocPositions[:, 0], self.etrocPositions[:, 1], 'g+')
        # Draw center
        ax[1].plot(self.center[0], self.center[1], 'kx')

##########################################################################################
def ComputePlacement_PCB(corners: np.array, module):
    place_pos = {}

    # Center in robot coordinates
    pcb_center = np.mean(corners, axis=0)
    horizontal = ((corners[2]-corners[0]) + (corners[3]-corners[1])) / 2
    theta_rad = np.arctan2(horizontal[1], horizontal[0])
    theta_deg = np.rad2deg(theta_rad)

    rotation = np.array([
        [np.cos(theta_rad), -np.sin(theta_rad)],
        [np.sin(theta_rad), np.cos(theta_rad)]
        ])

    # Correction to apply
    # Half size of ETROC + half gap between them
    correction_x = ETROC_SIZE[0] / 2 + ETROC_GAP / 2
    correction_y = ETROC_SIZE[1] / 2 + ETROC_GAP / 2
    
    # Different position require the correction in different directions
    local_positions = {
            "A" : np.array([-correction_x, +correction_y]),
            "B" : np.array([-correction_x, -correction_y]),
            "C" : np.array([+correction_x, +correction_y]),
            "D" : np.array([+correction_x, -correction_y])
            }

    for letter, local_position in local_positions.items():
        # Transform PCB coordinates -> robot coordinates
        position = pcb_center + rotation @ local_position
        # Apply global correction, if defined in robot coordinates
        position += np.array(CORRECTION)
        place_pos[f"PCB_{module}{letter}"] = [
            position[0],
            position[1],
            theta_rad
        ]

    return pcb_center, theta_rad, place_pos


def ComputeCenter_ETROC(corners: np.array, etroc_letter):
    """
    Robot reference frame --> x,y
    ETROC reference frame --> x',y'
    """
    # In x,y
    center = np.mean(corners, axis=0)

    # ETROC orientation 
    horizontal = ((corners[2] - corners[0]) + (corners[3] - corners[1])) / 2
    theta_rad = np.arctan2(horizontal[1], horizontal[0])
    theta_deg = np.rad2deg(theta_rad)

    # Correction defined in ETROC reference frame (x', y')
    correction = np.array(ETROC_CENTER_CORRECTION, dtype=float)
    # A/B and C/D have opposite correction directions
    if etroc_letter not in ("A", "B"):
        correction = -correction

    # Rotate correction from ETROC frame (x', y') to robot frame (x, y)
    rotation = np.array([
        [np.cos(theta_rad), -np.sin(theta_rad)],
        [np.sin(theta_rad),  np.cos(theta_rad)]
    ])
    correction_robot = rotation @ correction

    # Apply correction in robot reference frame
    center = center + correction_robot

    return [center[0], center[1], theta_rad]

######################################################################################

if __name__=='__main__':


    ETROCs = []
    #ETROCshifts = np.asarray([np.asarray([0.0, 0.0]), np.asarray([0.0, 0.0]), np.asarray([0.0, 0.0]), np.asarray([0.0, 0.0])])
    #ETROCrotations = [0.0, 0.0, 0.0, 0.0]
    ETROCshifts = np.asarray([np.asarray([0.1, -0.1]), np.asarray([0.2, 0.1]), np.asarray([-0.05, 0.0]), np.asarray([-0.2, -0.2])])
    ETROCrotations = [0.01, -0.02, 0.005, -0.01]
    for i in range(4):
        e = ETROC(nominalCornersETROC, nominalFiducialsETROC)
        e.move(ETROCPositionsInChuck[i] + ETROCshifts[i], ETROCrotations[i])
        ETROCs.append(e)


    PCBshifts = np.asarray([0.1, 0.1])   
    PCBrotation = 0.02
    #PCBshifts = np.asarray([0.1, -0.1])   
    #PCBrotation = -0.001
    pcb = PCB(nominalCornersPCB, nominalFiducialsPCB, ETROCPositionsInPCB)
    pcb.move(PCBPositionInChuck + PCBshifts, PCBrotation)
   


    fig, ax = plt.subplots(1, 2, figsize=(20, 10))

    for e in ETROCs:
        e.draw(ax[0])
    pcb.draw(ax[0])

    letters = ['A', 'B', 'C', 'D']
    measPositions_ = []
    measThetas_ = []
    for i, e in enumerate(ETROCs):
        x, y, theta = ComputeCenter_ETROC(e.fiducialMarks, letters[i])
        measPositions_.append(np.asarray([x, y]))
        print(f'Real center is at: ({e.center[0]}, {e.center[1]}), theta: {ETROCrotations[i]}')
        print(f'Measured center is at: ({x}, {y}), theta: {theta}')
    

    pcb_center, theta_rad, place_pos = ComputePlacement_PCB(pcb.fiducialMarks, 1)
    for i, epos in enumerate(pcb.etrocPositions):
        print(f'Real ETROC positions: ({epos[0]}, {epos[1]})')
        name = f'PCB_1{letters[i]}'
        print(f'Measured ETROC positions: ({place_pos[name][0]}, {place_pos[name][1]})')

  
    plt.show()


   




