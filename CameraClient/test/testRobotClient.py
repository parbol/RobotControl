from optparse import OptionParser
from CameraClient.RobotCamera import RobotCamera
import time  


if __name__ == "__main__":
    
    parser = OptionParser(usage="%prog --help")
    parser.add_option("-f", "--filenameinput",   dest="filenameinput",   type='string',  default="input.txt",       help="Name of the input interchange name.")
    parser.add_option("-i", "--ip",              dest="ip",              type='string',  default='172.16.110.151', help="IP of the server.")
    parser.add_option("-p", "--port",            dest="port",            type=int,       default=1999,             help="Port of the server.")
    (options, args) = parser.parse_args()

    client = RobotCamera(options.ip, options.port, options.filenameinput)
    time.sleep(4)
    client.takePic()
    time.sleep(4)
    client.takePic()
    client.stop()
