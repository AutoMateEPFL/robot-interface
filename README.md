[![CircleCI](https://circleci.com/gh/circleci/circleci-docs.svg?style=svg)](https://circleci.com/gh/AutoMateEPFL/robot-interface)
[![Maintainability](https://api.codeclimate.com/v1/badges/755d3fbdd32b369d58ae/maintainability)](https://codeclimate.com/github/AutoMateEPFL/robot-interface/maintainability) 
[![Test Coverage](https://api.codeclimate.com/v1/badges/755d3fbdd32b369d58ae/test_coverage)](https://codeclimate.com/github/AutoMateEPFL/robot-interface/test_coverage)

# AutoMate - Robot Interface

AutoMate's Robot Interface is a backend control system for the robotic platform, OneMate. This interface is responsible for managing all communication with the platform's peripherals, such as the gripper, camera, and the motion controller.

## Overview

### Concept
The workspace of the robot uses a grid system on the workplane, as illustrated below. Each grid location can store objects of varying heights, determined by the space requirements of the gripper.

*(Add image here)*

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


