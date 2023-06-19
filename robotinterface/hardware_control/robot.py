import json
import time
import types
import asyncio
from robotinterface.logistics.grid import Grid
from robotinterface.logistics.positions import GridPosition, CartesianPosition
from robotinterface.logistics.pickable import Pickable
from robotinterface.hardware_control import constants
from robotinterface.hardware_control.gripper import Gripper
from robotinterface.hardware_control.platform import Platform
from robotinterface.hardware_control.vision import Vision
import logging

log = logging.getLogger(__name__)

class Robot:
    """
    Represents a Robot for labautomation with a gripper and a camera.

    Attributes:
        platform: The connection to the GRBL controller.
        gripper: The connection to the gripper
        camera: The connection to the camera (if any).
        grid: The grid object representing the workspace of the robot.
    """

    @classmethod
    async def build(cls, grid: Grid):
        """
        Asynchronously builds a Robot instance.

        Args:
            grid (Grid): The grid object representing the workspace of the robot.

        Returns:
            Robot: The built Robot instance.
        """

        file_path = "hardware_control/FirmwareSettings/port-settings-laptop-silvio.json"
        with open(file_path, 'r') as f:
            data = json.load(f)

        gripper_task = None
        platform_task = None
        for setting in data["ComSettings"]:
            if setting["name"] == "dyna":
                gripper_task = asyncio.create_task(Gripper.build(setting))
            elif setting["name"] == "grbl":
                platform_task = asyncio.create_task(Platform.build(setting))

        camera_connection_task = asyncio.create_task(Vision.build())
        
        platform = None
        gripper = None
        camera = None

        # Excuting all the build tasks in parallel to reduce time
        if gripper_task and platform_task:
            gripper, platform, camera = await asyncio.gather(gripper_task, platform_task,
                                                                        camera_connection_task)
        elif gripper_task:
            gripper, camera = await asyncio.gather(gripper_task, camera_connection_task)
        elif platform_task:
            platform, camera = await asyncio.gather(platform_task, camera_connection_task)
        else:
            camera = await camera_connection_task


        return cls(platform, gripper, camera, grid)

    def __init__(self, platform: Platform, gripper: Gripper, camera, grid: Grid):
        """
        Initializes a new instance of the Robot class.

        Args:
            platform: The connection to the GRBL controller.
            gripper: The gripper of the robot.
            camera: The connection to the camera (if any).
            grid: The grid object representing the workspace of the robot.
        """
        self.gripper = gripper
        self.platform = platform
        self.camera = camera
        self.grid = grid

    async def _move_and_act(self, coordinates: CartesianPosition, action: types.FunctionType, action_after=lambda: None):
        """
        Moves the robot to the specified coordinates and performs an action.

        Args:
            coordinates: The target Cartesian coordinates.
            action: The action to perform at the target coordinates.
            action_after: The action to perform after returning to the clearance position (default: lambda: None).
        """
        logging.info(f"Moving to x:{coordinates.x}, y:{coordinates.y}, z:{coordinates.z}")
        await self.platform.move(coordinates.x, coordinates.y, constants.CLERANCE, constants.FEEDRATE)
        await self.platform.move(coordinates.x, coordinates.y, coordinates.z, constants.FEEDRATE)
        await action()
        await self.platform.move(coordinates.x, coordinates.y, constants.CLERANCE, constants.FEEDRATE)
        action_after()

    async def move(self, position: GridPosition, height=0):
        """
        Moves the robot to a specified grid position.

        Args:
            position: The target grid position.
            height: The desired height (default: 0).
        """
        coordinates = self.grid.get_coordinates_from_grid(position)
        await self.platform.move(coordinates[0], coordinates[1], height, constants.FEEDRATE)

    async def pick(self, objects: list[Pickable]):
        """
        Picks up objects from the grid.

        Args:
            objects: The objects to be picked up.
        """
        coordinates = self.grid.remove_object(objects)
        await self._move_and_act(coordinates, self.gripper.close)

    async def place(self, objects: list[Pickable], position: GridPosition):
        """
        Places objects on the grid at a specified position.

        Args:
            objects: The objects to be placed.
            position: The target grid position.
        """
        coordinates = self.grid.add_object(objects, position)
        await self._move_and_act(coordinates, self.gripper.open)

    async def pick_and_place(self, objects: list[Pickable], position: GridPosition):
        """
        Picks up objects and places them at a specified grid position.

        Args:
            objects: The objects to be picked up and placed.
            position: The target grid position.
        """
        await self.pick(objects)
        await self.place(objects, position)

    async def save_picture(self, obj: Pickable):
        """
        Takes a picture of a specified object.

        Args:
            obj: The object to take a picture of.
        """
        await self.platform.send_command("G56")
        await self.gripper.rotate(90)
        await self._move_and_act(self.grid.get_coordinates(obj), self.camera.save_picture)
        await self.gripper.rotate(0)
        await self.platform.send_command("G55")


    async def shutdown(self):
        """
        Shuts down the robot by moving to the home position and shutting down the gripper.
        """
        logging.info("Shutting down robot")
        await self.platform.send_command("G54")
        await self.platform.move(0.0, 0.0, 0.0, constants.FEEDRATE)
        await self.gripper.shutdown()
        await self.camera.shutdown()
