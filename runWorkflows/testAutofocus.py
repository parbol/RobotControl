from optparse import OptionParser

from CameraClient.RobotCamera import RobotCamera
from RobotBrain.AutoFocusController import AutoFocusController
from RobotBrain.RobotController import RobotController


if __name__ == "__main__":

    parser = OptionParser(usage="%prog --help")
    parser.add_option("-i", "--ip", dest="ip", type="string", default="192.168.0.189", help="IP of the camera server.")
    parser.add_option("-p", "--port", dest="port", type=int, default=8080, help="Port of the camera server.")
    parser.add_option("-d", "--device", dest="device", type="string", default="/dev/ttyUSB0", help="Robot device name.")
    parser.add_option("-b", "--bauds", dest="bauds", type=int, default=115200, help="Robot bauds.")
    parser.add_option("-m", "--move-to-focus", dest="move_to_focus", action="store_true", default=False, help="Move robot to estimated focus at the end.")
    (options, args) = parser.parse_args()

    focus_position = (434.815, -147.438, 127.388, -72.23)
    autofocus_velocity = 10.0
    autofocus_range = 1.0

    robot_camera = RobotCamera(options.ip, options.port, "picture.png", None)
    robot_controller = RobotController(options.device, options.bauds, robot_camera, None, True)
    autofocus_controller = AutoFocusController(robot_controller, robot_camera)

    print("Autofocus input position:", focus_position)
    print("Autofocus range:", autofocus_range)
    print("Autofocus velocity:", autofocus_velocity)
    print("Move to focus:", options.move_to_focus)
    print("Robot initial velocity:", robot_controller.get_velocity())
    print("Robot initial position XYZ:", robot_controller.getPositionXYZ())

    try:
        summary, focus_z, fraction = autofocus_controller.start_AutoFocus(
            focus_position,
            autofocus_range,
            autofocus_velocity,
            move_toFocus=options.move_to_focus,
        )

        print("Autofocus summary:", summary)
        print("Estimated focus fraction:", fraction)
        print("Estimated focus z:", focus_z)
        print("Robot final velocity:", robot_controller.get_velocity())
        print("Robot final position XYZ:", robot_controller.getPositionXYZ())
    finally:
        robot_controller.stop()
