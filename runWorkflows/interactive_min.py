import socket

from CameraClient.RobotCamera import RobotCamera
from RobotBrain.RobotController import RobotController


class InteractiveRobotController(RobotController):
    def __init__(self, device, bauds, camera_client, robot_model=None, debug=False):
        self.camera = camera_client
        super().__init__(device, bauds, camera_client, robot_model, debug)

    def exit(self):
        try:
            self.serial.close()
        except Exception:
            pass
        raise RuntimeError("RobotController requested exit")


class InteractiveControl:
    def __init__(
        self,
        camera_ip="192.168.0.189",
        camera_port=8080,
        robot_device="/dev/ttyUSB0",
        robot_bauds=115200,
        picture_path="picture.png",
        debug=False,
    ):
        self.robot_device = robot_device
        self.robot_bauds = robot_bauds
        self.debug = debug
        self.robot_model = None
        self.camera_client = RobotCamera(
            camera_ip,
            camera_port,
            picture_path,
            self.robot_model,
        )

    def take_picture(self, picture_path=None):
        if picture_path is not None:
            self.camera_client.changeFileName(picture_path)
        self.camera_client.takePic()
        return self.camera_client.fileName

    def move_robot(self, x, y, z, rz, velocity=None, orientation="s"):
        robot_controller = None
        try:
            robot_controller = InteractiveRobotController(
                self.robot_device,
                self.robot_bauds,
                self.camera_client,
                self.robot_model,
                self.debug,
            )
            if velocity is not None:
                robot_controller.changeVelocity(velocity)
            moved = robot_controller.goTo(x, y, z, rz, orientation=orientation)
            return moved, robot_controller.getPositionXYZ()
        finally:
            self._close_robot_controller(robot_controller)

    def close(self):
        try:
            self.camera_client.sendMessage("STOP")
        except Exception:
            pass
        try:
            self.camera_client.s.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass
        try:
            self.camera_client.s.close()
        except Exception:
            pass

    def _close_robot_controller(self, robot_controller):
        if robot_controller is None:
            return
        try:
            robot_controller.sendMessage("STOP:")
        except Exception:
            pass
        try:
            robot_controller.serial.close()
        except Exception:
            pass
