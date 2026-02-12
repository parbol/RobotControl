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

## ExperimentalSetup

This package contains a model of the table, robot and physical camera. It basically takes care of translating between camera coordinates and 3D coordinates.

## runWorkflows

This should have the executables implementing the calibration and assembly workflows.

