[![CircleCI](https://circleci.com/gh/circleci/circleci-docs.svg?style=svg)](https://circleci.com/gh/AutoMateEPFL/robot-interface)
[![Maintainability](https://api.codeclimate.com/v1/badges/755d3fbdd32b369d58ae/maintainability)](https://codeclimate.com/github/AutoMateEPFL/robot-interface/maintainability) 
[![Test Coverage](https://api.codeclimate.com/v1/badges/755d3fbdd32b369d58ae/test_coverage)](https://codeclimate.com/github/AutoMateEPFL/robot-interface/test_coverage)

# AutoMate - Robot Interface
<p align="center">
<img src="https://github.com/AutoMateEPFL/robot-interface/assets/16036727/f08f9100-398f-4c9b-a025-1d1bf1a9efb5" width="500">
</p>

AutoMate's Robot Interface is a backend control system for the robotic platform, OneMate. This interface manages all communication with the platform's peripherals, such as the gripper, camera, and motion controller.

## Overview

The robot's workspace is built around a grid system on the workplane, as demonstrated below. Each grid cell can store objects of varied heights, akin to stacking four Petri dishes atop each other, as illustrated in the figure below. The size and requirements of the gripper determine the grid's spacing.

<p align="center">
 <img src="https://github.com/AutoMateEPFL/robot-interface/assets/16036727/85899569-fa89-488f-9008-7de8bfe0dd80" width="500">
</p>

### Positional Classes

We use two classes to denote the physical positions of objects. The `GridPosition` class represents a 2D location on the discretized grid. In contrast, the `CartesianPosition` class denotes the 3D location of an object within the motion controller's coordinates.

### Manipulatable Objects

Python objects represent all objects the robot should interact with and are subclasses of the `Pickable` class. For example, as the robot must manipulate the upper and lower parts of a petri dish separately, they are modeled as individual objects.

Objects are added to the grid to mirror the robot's physical reality. For instance, in the above image, the grid representation would look like this:

```python
bottom = SmallPetriBottom()
top = SmallPetriTop()

grid.add_object([bottom, top], GridPosition(1, 1))
```
### Basic Operations
The Robot Interface provides four fundamental operations for the objects placed within the robot's workspace:

* Pick: This operation allows the robot to pick up an object from a grid position, retaining it in the gripper.
* Place: The robot can place an object the gripper holds at a designated grid location. The backend system then determines the current position of the stack where the object will be placed.
* Pick & Place: This operation involves picking up an object and placing it at a new location.
* Taking Picture: This operation positions the end effector so that a picture of a grid position can be captured.

## Getting Started


This project uses [Poetry](https://python-poetry.org/docs/), a Python dependency management tool. If you haven't installed Poetry yet, please follow the [official installation guide](https://python-poetry.org/docs/).

Once you have Poetry installed, you can install the project using the following command in your terminal:

```bash
poetry install
```


Before running the project, you need to update the `robotinterface/hardware_control/FirmwareSettings/hardware_settings.json` file with the correct settings for your serial ports. 

You can identify the correct ports using different tools. For the gripper, consider using the [DYNAMIXEL Wizard](https://emanual.robotis.com/docs/en/software/dynamixel/dynamixel_wizard2/). For the motion controller, [OpenBuilds CONTROL](https://software.openbuilds.com/) is recommended.


```bash
poetry run python -m robotinterface\protocol.py
```

## Docker
As an alternative to the direct installation, you can use the provided Docker image to avoid any direct installation on your machine. For this, you need to pull the latest docker image from the docker repository of ***AutoMateEPFL*** . For this, you first have to log in to the docker registry. Where you have to replace the [ACCESSTOKEN](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) and the USERNAME. The personal access token only needs the rights write:packages / read:packages.
```bash
echo ACESSTOKEN | docker login ghcr.io -u USERNAME --password-stdin
```
Then you can pull the docker image. The docker image is built for two versions for arm64 and amd64 to so that the image can also be run on a Raspberry Pi. 

```bash
docker pull ghcr.io/automateepfl/robot-interface:latest
```
The correct serial ports for the controllers and the camera must be passed to the docker image with the following command to run it. This passthrough only works on linux machines currently. If Vision is used the camera must be passed through as well.


```bash
docker run -it --device=/dev/ttyUSB0 --device=/dev/ttyUSB1 IMAGEID bash
```

Then inside the docker container, the main protocol can be run by calling. 

```bash
python -m robotinterface.protocol.py
```


