# RobotControl

This package controls the assembly workflows of the CMS ETL modules at IFCA.

The package has several logic units dedicated to different parts of the assembly:

## CameraServer

This package takes care of taking pictures from the camera and sending them to the Robot camera client.

This has to run in the raspberry pi

## CameraClient

This package takes care of communicating with the camera server in the raspberry pi and processing the images

## RobotBrain

This package communicates with the CS9 and sends commands to move, open/close vacuum lines, etc.

Also, the ETLController is implemented where specific ETL functions and movements are defined

## ExperimentalSetup

This package contains a model of the table, robot and physical camera. It basically takes care of translating between camera coordinates and 3D coordinates.

## runWorkflows

This should have the executables implementing the calibration and assembly workflows.

## How to work with it?
1) Run the wanted script or connect to the Robot Controller
'''
rc = RobotController.RobotController("/dev/ttyUSB1", 115200, "")
'''
2) Using the tablet, go to ETL and start connection.
- Now, the handshake should be done
3) Send the wanted messages
