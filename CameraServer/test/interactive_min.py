# control_minimo.py
import socket
from CameraClient.RobotCamera import RobotCamera
from RobotBrain.RobotController import RobotController

class ControlMinimo:
    def __init__(self, ip_cam, port_cam, device_robot, bauds=115200, foto_out="foto.png", debug=False):
        self.cameraCliente = RobotCamera(ip_cam, port_cam, foto_out, robot3D=None)
        self.robot = RobotController(device_robot, bauds, self.cameraCliente, robot3D=None, debug=debug)

        # Workaround: RobotController.exit() usa self.camera, pero en __init__ no la asigna
        self.robot.camera = self.cameraCliente

    def tomar_foto(self, ruta=None):
        if ruta:
            self.cameraCliente.changeFileName(ruta)
        self.cameraCliente.takePic()
        return self.cameraCliente.fileName

    def mover_robot(self, x, y, z, rz, velocidad=None, orientation="s"):
        if velocidad is not None:
            self.robot.changeVelocity(velocidad)  # 0..100
        ok = self.robot.goTo(x, y, z, rz, orientation=orientation)
        return ok, self.robot.getPositionXYZ()

    def estado_robot(self):
        self.robot.askStatus()
        return {
            "xyz": self.robot.getPositionXYZ(),
            "j1j2j3": self.robot.getPositionJ1J2J3(),
            "valves": self.robot.getValveStatus(),
            "em": self.robot.getEM(),
        }

    def cerrar(self):
        # Cierre sin sys.exit(), para seguir en REPL
        try:
            self.robot.sendMessage("STOP:")
        except Exception:
            pass
        try:
            self.cameraCliente.sendMessage("STOP")
        except Exception:
            pass
        try:
            self.robot.serial.close()
        except Exception:
            pass
        try:
            self.cameraCliente.s.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass
        try:
            self.cameraCliente.s.close()
        except Exception:
            pass
