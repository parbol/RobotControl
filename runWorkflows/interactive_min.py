import socket
import time

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

    def stop_remote_mode(self, timeout_seconds=3.0):
        self.sendMessage("STOP:")
        reply = self._read_optional_robot_message(timeout_seconds)
        if reply:
            self.decodeMessage(reply)
        return reply

    def _read_optional_robot_message(self, timeout_seconds):
        deadline = time.time() + timeout_seconds
        text = ""
        while time.time() < deadline and len(text) < self.msg_length:
            chunk = self.serial.read(self.msg_length - len(text))
            if not chunk:
                continue
            text += chunk.decode()
            if "XXXXX" in text:
                break
        if "@@@@@" not in text or "XXXXX" not in text:
            return None
        return text[text.find("@@@@@") + 5:text.find("XXXXX")]


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
            robot_controller.stop_remote_mode()
        except Exception:
            pass
        try:
            robot_controller.serial.close()
        except Exception:
            pass



#from runWorkflows.interactive_min import InteractiveControl
#control = InteractiveControl()
#
#control.take_picture("picture_001.png")
#
#control.camera_client.auto_exposureSaturation(0.001, 0.0001)
#
#control.camera_client.set_exposure(1/1024)
#
#control.camera_client.change_binningRuntime(bx=2, by=2)
#
#control.move_robot(x=434.815, y=-147.438, z=127.388, rz=-72.23, velocity=50.0)
#
#control.camera_client.start_autofocusAcquisition(max_photos=100, time_photo=0.0)
#control.camera_client.stop_autofocusAcquisition()
#
#control.close()

