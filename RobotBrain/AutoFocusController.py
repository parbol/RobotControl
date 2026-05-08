#      /$$$$$$  /$$   /$$ /$$$$$$$$ /$$$$$$           
#     /$$__  $$| $$  | $$|__  $$__//$$__  $$          
#    | $$  \ $$| $$  | $$   | $$  | $$  \ $$          
#    | $$$$$$$$| $$  | $$   | $$  | $$  | $$          
#    | $$__  $$| $$  | $$   | $$  | $$  | $$          
#    | $$  | $$| $$  | $$   | $$  | $$  | $$          
#    | $$  | $$|  $$$$$$/   | $$  |  $$$$$$/          
#    |__/  |__/ \______/    |__/   \______/           
                                                                                                                            
#     /$$$$$$$$ /$$$$$$   /$$$$$$  /$$   /$$  /$$$$$$ 
#    | $$_____//$$__  $$ /$$__  $$| $$  | $$ /$$__  $$
#    | $$     | $$  \ $$| $$  \__/| $$  | $$| $$  \__/
#    | $$$$$  | $$  | $$| $$      | $$  | $$|  $$$$$$ 
#    | $$__/  | $$  | $$| $$      | $$  | $$ \____  $$
#    | $$     | $$  | $$| $$    $$| $$  | $$ /$$  \ $$
#    | $$     |  $$$$$$/|  $$$$$$/|  $$$$$$/|  $$$$$$/
#    |__/      \______/  \______/  \______/  \______/ 


import time
import math

from CameraClient.RobotCamera import RobotCamera


class AutoFocusController:
    def __init__(self, robot, camera):
        self.robot = robot
        self.camera = camera
        self.showBanner()


    def start_AutoFocus(self, position, z_range, z_speed, move_toFocus = False):
        # move to position but z = position("z")+z_range/2 (start position of autofocus)
        if isinstance(position, dict):
            x = position["x"]
            y = position["y"]
            z = position["z"]
            rz = position["rz"]
        else:
            x, y, z, rz = position

        start_z = z + z_range / 2
        end_z = z - z_range / 2
        self.robot.safeMovement(x, y, start_z, rz)

        # init camera autofocus_acquisition
        if not self.camera.start_autofocusAcquisition():
            raise RuntimeError("Could not start autofocus acquisition")

        # move to position but z = position("z")-z_range/2 and speed = z_speed
        stored_speed = self.robot.robotcontroller.get_velocity()
        self.robot.robotcontroller.changeVelocity(z_speed)

        summary = None
        try:
            self.robot.safeMovement(x, y, end_z, rz)
        # stop autofocus_acquisition and get summary
        finally:
            summary = self.camera.stop_autofocusAcquisition()

        fraction = self.camera.estimate_focusFraction()
        focus_z = start_z - fraction * z_range

        # Go back to prev. speed and move to estimated focus
        self.robot.robotcontroller.changeVelocity(stored_speed)

        if move_toFocus == True:
            self.robot.safeMovement(x, y, focus_z, rz)

        return summary, focus_z, fraction
    def showBanner(self):
        print('      /$$$$$$  /$$   /$$ /$$$$$$$$ /$$$$$$')
        print('     /$$__  $$| $$  | $$|__  $$__//$$__  $$')          
        print('    | $$  \ $$| $$  | $$   | $$  | $$  \ $$')          
        print('    | $$$$$$$$| $$  | $$   | $$  | $$  | $$')          
        print('    | $$__  $$| $$  | $$   | $$  | $$  | $$')          
        print('    | $$  | $$| $$  | $$   | $$  | $$  | $$')          
        print('    | $$  | $$|  $$$$$$/   | $$  |  $$$$$$/')          
        print('    |__/  |__/ \______/    |__/   \______/ ')          
        print('')                                                                                                                           
        print('     /$$$$$$$$ /$$$$$$   /$$$$$$  /$$   /$$  /$$$$$$') 
        print('    | $$_____//$$__  $$ /$$__  $$| $$  | $$ /$$__  $$')
        print('    | $$     | $$  \ $$| $$  \__/| $$  | $$| $$  \__/')
        print('    | $$$$$  | $$  | $$| $$      | $$  | $$|  $$$$$$ ')
        print('    | $$__/  | $$  | $$| $$      | $$  | $$ \____  $$')
        print('    | $$     | $$  | $$| $$    $$| $$  | $$ /$$  \ $$')
        print('    | $$     |  $$$$$$/|  $$$$$$/|  $$$$$$/|  $$$$$$/')
        print('    |__/      \______/  \______/  \______/  \______/ ')
