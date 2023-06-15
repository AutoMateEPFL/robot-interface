import json
import time
import types
from robotinterface.logistics.grid import Grid
from robotinterface.logistics.positions import GridPosition, CartesianPosition
from robotinterface.logistics.pickable import Pickable
from robotinterface.hardware_control import constants
from robotinterface.hardware_control.gripper import Gripper
from robotinterface.hardware_control.platform import Platfrom
import logging

log = logging.getLogger(__name__)

class Robot:
    """
    Represents a Robot for labautomation with a gripper and a camera.

    Attributes:
        platfrom: The connection to the GRBL controller.
        gripper: The connection to the gripper
        camera_connection: The connection to the camera (if any).
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

        platfrom = None
        camera_connection = None
        gripper = None

        file_path = "hardware_control/FirmwareSettings/port-settings-laptop-silvio.json"
        with open(file_path, 'r') as f:
            data = json.load(f)

        for setting in data["ComSettings"]:
            if setting["name"] == "dyna":
                gripper = await Gripper.build(setting)

            elif setting["name"] == "grbl":
                platfrom = await Platfrom.build(setting)

        return cls(platfrom, gripper, camera_connection, grid)

    def __init__(self, platfrom: Platfrom, gripper: Gripper, camera_connection, grid: Grid):
        """
        Initializes a new instance of the Robot class.

        Args:
            platfrom: The connection to the GRBL controller.
            gripper: The gripper of the robot.
            camera_connection: The connection to the camera (if any).
            grid: The grid object representing the workspace of the robot.
        """
        self.gripper = gripper
        self.platfrom = platfrom
        self.camera_connection = camera_connection
        self.grid = grid

    async def _move_and_act(self, coordinates: CartesianPosition, action: types.FunctionType, action_after=lambda: None):
        """
        Moves the robot to the specified coordinates and performs an action.

        Args:
            coordinates: The target Cartesian coordinates.
            action: The action to perform at the target coordinates.
            action_after: The action to perform after returning to the clearance position (default: lambda: None).
        """
        await self.platfrom.move(coordinates.x, coordinates.y, constants.CLERANCE, constants.FEEDRATE)
        await self.platfrom.move(coordinates.x, coordinates.y, coordinates.z, constants.FEEDRATE)
        action()
        await self.platfrom.move(coordinates.x, coordinates.y, constants.CLERANCE, constants.FEEDRATE)
        action_after()

    async def move(self, position: GridPosition, height=0):
        """
        Moves the robot to a specified grid position.

        Args:
            position: The target grid position.
            height: The desired height (default: 0).
        """
        coordinates = self.grid.get_coordinates_from_grid(position)
        await self.platfrom.move(coordinates[0], coordinates[1], height, constants.FEEDRATE)

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

    async def take_picture(self, obj: Pickable):
        """
        Takes a picture of a specified object.

        Args:
            obj: The object to take a picture of.
        """
        await self.platfrom.send_command("G56")
        await self.gripper.rotate(90)
        await self._move_and_act(self.grid.get_coordinates(obj), self._take_picture)
        await self.gripper.rotate(0)
        await self.platfrom.send_command("G55")

    def _take_picture(self):
        """
        Private method to simulate taking a picture.
        """
        time.sleep(2)

    async def shutdown(self):
        """
        Shuts down the robot by moving to the home position and shutting down the gripper.
        """
        await self.platfrom.send_command("G54")
        await self.platfrom.move(0.0, 0.0, 0.0, constants.FEEDRATE)
        await self.gripper.shutdown()
