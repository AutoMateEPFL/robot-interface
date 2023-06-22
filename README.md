[![CircleCI](https://circleci.com/gh/circleci/circleci-docs.svg?style=svg)](https://circleci.com/gh/AutoMateEPFL/robot-interface)
[![Maintainability](https://api.codeclimate.com/v1/badges/755d3fbdd32b369d58ae/maintainability)](https://codeclimate.com/github/AutoMateEPFL/robot-interface/maintainability) 
[![Test Coverage](https://api.codeclimate.com/v1/badges/755d3fbdd32b369d58ae/test_coverage)](https://codeclimate.com/github/AutoMateEPFL/robot-interface/test_coverage)

# AutoMate - Robot Interface
<p align="center">
<img src="https://github.com/AutoMateEPFL/robot-interface/assets/16036727/f08f9100-398f-4c9b-a025-1d1bf1a9efb5" width="500">
</p>

AutoMate's Robot Interface is a backend control system for the robotic platform, OneMate. This interface manages all communication with the platform's peripherals, such as the gripper, camera, and the motion controller.

## Concept

The robot's workspace uses a grid system on the workplane, as illustrated below. Each grid location can store objects of varying heights. The figure below, this is shown four petri dishes that are stacked on top of each other. The space requirements of the gripper determine the spacing of the grid. 

<p align="center">
 <img src="https://github.com/AutoMateEPFL/robot-interface/assets/16036727/85899569-fa89-488f-9008-7de8bfe0dd80" width="500">
</p>

### Locations


### Manupilatable Objects

A Python object represents all the objects the robot should be able to manipulate individually. All those objects are subclasses of the Pickable class. As the robot must be able to manipulate the upper and lower part of the petri dish separately they are individual objects:


These objects must be added to the grid to represent the physical reality of the robot. For the example in picture one, it would look like this.


## Getting Started

### Prerequisites
Before installation, you need to update the `robotinterface/hardware_control/FirmwareSettings/hardware_settings.json` file with the correct settings for your serial ports. 

You can identify the correct ports using different tools. For the gripper, consider using the [DYNAMIXEL Wizard](https://emanual.robotis.com/docs/en/software/dynamixel/dynamixel_wizard2/). For the motion controller, [OpenBuilds CONTROL](https://software.openbuilds.com/) is recommended.

### Installation

This project uses [Poetry](https://python-poetry.org/docs/), a Python dependency management tool. If you haven't installed Poetry yet, please follow the [official installation guide](https://python-poetry.org/docs/).

Once you have Poetry installed, you can install the project using the following command in your terminal:

```bash
poetry install
```

You can then run the standard protocol with:

```bash
poetry run python -m robotinterface\protocol.py
```

## Docker
As an alternative to the direct installation, you can use the provided Docker image to avoid any direct installation on your machine.

## Motioncontroller Firmware


