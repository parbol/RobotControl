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
from RobotBrain.RobotController import RobotController


class AutoFocusController:
    def __init__(self, robot, camera):
        self.robot = robot
        self.camera = camera


    def start_AutoFocus(self, position, z_range, z_speed):
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
        self.robot.goTo(x, y, start_z, rz)

        # init camera autofocus_acquisition
        if not self.camera.start_autofocusAcquisition():
            raise RuntimeError("Could not start autofocus acquisition")

        # move to position but z = position("z")+z_range/2 and speed = z_speed
        previous_velocity = getattr(self.robot, "velocity", None)
        if z_speed is not None:
            self.robot.changeVelocity(z_speed)

        summary = None
        try:
            self.robot.goTo(x, y, end_z, rz)
        # stop autofocus_acquisition and get summary
        finally:
            summary = self.camera.stop_autofocusAcquisition()
            if previous_velocity is not None:
                self.robot.changeVelocity(previous_velocity)

        return summary
