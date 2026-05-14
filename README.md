# RobotControl

This package controls the assembly workflows of the CMS ETL modules at IFCA.
It provides tools for:

* Robot motion control
* Camera acquisition and image processing
* Coordinate transformations
* Automated assembly workflows
* ETL-specific robotic operations


## Project Structure

### CameraServer

This package takes care of taking pictures from the camera and sending them to the Robot camera client.

This has to run in the Raspberry Pi connected to the camera.

### CameraClient

This package takes care of communicating with the camera server in the Raspberry Pi and processing the images.

### RobotBrain

This is dicided into two control layers:
* RobotController: This is the basic control layer, where the comunication with the robot is implemented. It has basic functions to move the robot, open/close vacuum lines, etc.

* ETLController: This is the high level control layer, where specific ETL functions and movements are defined. It uses the RobotController to send the commands to the robot, but it has more complex functions like `safeMovement` or `fullAutoFocus` that are needed for the ETL assembly.

### ExperimentalSetup

This package contains a model of the:
* Table
* Robot
* physical camera. 

It basically takes care of translating between camera coordinates and 3D coordinates.

### runWorkflows

This should have the executables implementing the calibration and assembly workflows.

The RobotControl scripts handles the basic comunication with the robot. While the ETLController handle ETL specific and more complex functions.

## How to work with it?
1) Setup everything needed:
```bash
python3 -m pip install -r requirements.txt
source setup.sh
```

2) Connect to the raspberry (Camera controller) and run the server there:
```python
python3 testCameraServer.py -i 192.168.0.189 -p 8080
```
3) Initialize the camera locally:
```python
robotCamera = RobotCamera(options.ip, options.port, 'picture.png', robot3D)
```
Now the connection between the camera and the computer is working.

4) Connect to the Robot
* Via the Robot Controller
```python
robotcontroller = RobotController(device, bauds, camera, robot3D, debug)
```
* Or via the ETL Controller for predefined complex functions
```python
etlcontroller = ETLController(options.device, options.bauds, None, robot3D, False)
```
It will automatically test that the robot arm is in the correct orientation (left handed) and place it as it should be. 

Also, it has defined a safe movement (`safeMovement`), checking in which part of the table the robot is (referenced to the ETL plate position) and moves safely between them. For that both angular and cartesians movements are used.

2) Using the tablet, go to ETL and start connection.
- Now, the handshake should be done
3) Send the wanted messages/Run the wanted program


## Functionalities

### `ETLController`

The main ETL-specific functionalities are implemented in `ETLController.py`.

---

### Movement (`safeMovement`)

A controlled movement algorithm is implemented to avoid collisions during robot motion.

#### Algorithm

1. Move the robot to a predefined safe `Z` position (`180 mm`).
2. Determine:
   - The current ETL plate
   - The destination ETL plate

3. If the robot is moving between different plates, the movement follows:

```text
Current Position
    → Current Plate Safe Position
    → Destination Plate Safe Position
    → Final Position
```
- The movement between safe positions is performed using angular movements:
  1. First without changing `RZ`
  2. Then adjusting `RZ` at the destination safe position

4. If the robot remains on the same plate, it moves directly to the final position.

5. Final positioning is performed in the following order:
   1. Move in `(X, Y)`
   2. Rotate `RZ`
   3. Move in `Z`

---

### Rotate RZ (`rotateRZ`)

A controlled `RZ` rotation algorithm is implemented to avoid entanglement of:

- Raspberry Pi cabling
- LED light cables

#### Algorithm

1. If the current `RZ` angle is negative:
   - Move first to `RZ = 0°` or `RZ = 180°`
   - Select whichever is closer

2. If the target `RZ` angle is negative:
   - Again pass through `RZ = 0°` or `RZ = 180°`

3. Move to the final `RZ` position.

---

### Autofocus Algorithm (`fullAutoFocus`)

This algorithm automatically finds the optimal `Z` position for image acquisition.

#### Algorithm

1. Assuming the robot is placed at the desired:
   - `X`
   - `Y`
   - `RZ`

2. Move the robot to an estimated `Z` position. It has to be close enough to the optimal focus.

3. Compute the focus scan range limits.

4. Move continuously through the range while:
   - Capturing images
   - Computing image sharpness using the **Tenengrad variance**
   - Storing:
     - The time when the picture was taken
     - The image sharpness value

5. Once the scan is complete:
   - Determine the time corresponding to the maximum sharpness interpolating between the captured data points.
   - Compute the optimal focus `Z` assuming uniform robot velocity during the scan.