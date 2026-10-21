import numpy as np



mm = 1.0
ETROC_CENTER_CORRECTION = [0.00*mm, 0.00*mm]
ETROC_SIZE = [23*mm, 21*mm]
ETROC_GAP = 0.2*mm
# CORRECTION = [0*mm, -0.5*mm]
CORRECTION = [0*mm, 0*mm]


nominal0ETROC = np.asarray([2.50, -1.0]) + np.asarray([-23.0/2.0, 21.0/2.0])
nominal1ETROC = np.asarray([2.50, -20.0]) + np.asarray([-23.0/2.0, 21.0/2.0])
nominal2ETROC = np.asarray([22.0, -1.0]) + np.asarray([-23.0/2.0, 21.0/2.0])
nominal3ETROC = np.asarray([22.0, -20.0]) + np.asarray([-23.0/2.0, 21.0/2.0])


nominal0PCB = np.asarray([2.0, -2.5]) + np.asarray([-57.5/2.0, 44.1/2.0])
nominal1PCB = np.asarray([2.0, -41.6]) + np.asarray([-57.5/2.0, 44.1/2.0])
nominal2PCB = np.asarray([55.5, -2.5]) + np.asarray([-57.5/2.0, 44.1/2.0])
nominal3PCB = np.asarray([55.5, -41.6]) + np.asarray([-57.5/2.0, 44.1/2.0])



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





def realPositionETROC(d, r):

    P0ETROC = d + r @ nominal0ETROC
    P1ETROC = d + r @ nominal1ETROC
    P2ETROC = d + r @ nominal2ETROC
    P3ETROC = d + r @ nominal3ETROC

    return np.array([P0ETROC, P1ETROC, P2ETROC, P3ETROC])


def realPositionPCB(d, r):

    P0PCB = d + r @ nominal0PCB
    P1PCB = d + r @ nominal1PCB
    P2PCB = d + r @ nominal2PCB
    P3PCB = d + r @ nominal3PCB

    return np.array([P0PCB, P1PCB, P2PCB, P3PCB])




if __name__=='__main__':

    ETROC_theta_rad = -0.005
    ETROC_rotation = np.array([
        [np.cos(ETROC_theta_rad), -np.sin(ETROC_theta_rad)],
        [np.sin(ETROC_theta_rad), np.cos(ETROC_theta_rad)]
        ])
    ETROC_pos = np.asarray([100.0, -500.0])

    PCB_theta_rad = -0.00
    PCB_rotation = np.array([
        [np.cos(PCB_theta_rad), -np.sin(PCB_theta_rad)],
        [np.sin(PCB_theta_rad), np.cos(PCB_theta_rad)]
        ])
    PCB_pos = np.asarray([-100.0, -500.0])


    ETROC_pos = realPositionETROC(ETROC_pos, ETROC_rotation)
    PCB_pos = realPositionPCB(PCB_pos, PCB_rotation)


    for i, pos in enumerate(ETROC_pos):
        print(f'ETROC {i}: ({pos[0]}, {pos[1]})')
    for i, pos in enumerate(PCB_pos):
        print(f'PCB {i}: ({pos[0]}, {pos[1]})')
        

    center, angle, pos = ComputePlacement_PCB(PCB_pos, '1')
    print(center)
    print(angle)
    for i in pos.items():
        print(i)





