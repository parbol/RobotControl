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

class AutoFocusController:
    def __init__(self, etlrobot):
        self.robot = etlrobot


    def start_AutoFocus(self, z_range, z_speed, move_toFocus = False):
        # XXX - Assuming XY and RZ positions are ok
        # move to position but z = position("z")+z_range/2 (start position of autofocus)
        start_z = z + z_range / 2
        end_z = z - z_range / 2

        self.robot.changeZ(start_z)

        # init camera autofocus_acquisition
        if not self.camera.start_autofocusAcquisition():
            raise RuntimeError("Could not start autofocus acquisition")

        # move to position but z = position("z")-z_range/2 and speed = z_speed
        stored_speed = self.robot.get_velocity()
        self.robot.changeVelocity(z_speed)

        summary = None
        try:
            self.robot.changeZ(end_z)
        # stop autofocus_acquisition and get summary
        finally:
            summary = self.camera.stop_autofocusAcquisition()

        fraction = self.camera.estimate_focusFraction()
        focus_z = start_z - fraction * z_range

        # Go back to prev. speed and move to estimated focus
        self.robot.changeVelocity(stored_speed)

        if move_toFocus == True:
            self.robot.changeZ(focus_z)

        return summary, focus_z, fraction
