import json
import time
import types
from robotinterface.drivers.dynamixel.controller import Dynamixel
from robotinterface.drivers.grbl.controller import GrblDriver
from robotinterface.logistics.grid import Grid
from robotinterface.logistics.positions import GridPosition, CartesianPosition
from robotinterface.logistics.pickable import Pickable
from robotinterface.hardware_control import constants
from robotinterface.hardware_control.gripper import Gripper
import logging

log = logging.getLogger(__name__)

class Robot:
    """
    Represents a Robot for labautomation with a gripper and a camera.

    Attributes:
        grbl_connection: The connection to the GRBL controller.
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

        grbl_connection = None
        camera_connection = None
        gripper = None

        file_path = "hardware_control/FirmwareSettings/port-settings-laptop-silvio.json"  # replace this with your actual file path
        with open(file_path, 'r') as f:
            data = json.load(f)

        for setting in data["ComSettings"]:
            if setting["name"] == "dyna":

                ids = []
                for motor in setting['motors']:
                    ids.append(motor['id'])
                ids.sort()
                dyna_connection = Dynamixel(ids, "Robot_1", setting["port"], setting["bauderate"],
                                            ['xl' for _ in range(len(ids))])

                # set correct operating mode
                id_gripper = None
                id_rotation = None
                zero = None

                for motor in setting['motors']:
                    id = motor["id"]
                    name = motor["name"]

                    # Match the motor name for gripper and rotation
                    match name:
                        case "grip":
                            id_gripper = id
                            dyna_connection.set_operating_mode("pwm", id_gripper)
                        case "rot":
                            id_rotation = id
                            zero = motor["zero_pos"]
                            dyna_connection.set_operating_mode("position", id_rotation)
                        case _:
                            log.error(f"Unknown motor name: {name}")

                gripper = Gripper(dyna_connection, id_gripper, id_rotation, zero)

            elif setting["name"] == "grbl":
                grbl_connection = await GrblDriver.build(setting["port"], setting["bauderate"])
                await grbl_connection.home()
                # Set the origin of the G55 coordinate system to the workplane and shift so the camera still could
                # still take a picture of the origin
                await grbl_connection.send_command(f"G10 L2 P2 X-{setting['x_offset_camera']} Y0 Z{setting['z_offset']}")
                
                # Set the origin of the G56 coordinate system such that the camera can take a picture of the origin when moving to X0 Y0 Z0
                await grbl_connection.send_command(f"G10 L2 P3 X0 Y0 Z{setting['z_offset_camera']}")
                await grbl_connection.send_command("G55")

        return cls(grbl_connection, gripper, camera_connection, grid)

    def __init__(self, grbl_connection: GrblDriver, gripper: Gripper, camera_connection, grid: Grid):
        """
        Initializes a new instance of the Robot class.

        Args:
            grbl_connection: The connection to the GRBL controller.
            gripper: The gripper of the robot.
            camera_connection: The connection to the camera (if any).
            grid: The grid object representing the workspace of the robot.
        """
        self.gripper = gripper
        self.grbl_connection = grbl_connection
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
        await self.grbl_connection.move(coordinates.x, coordinates.y, constants.CLERANCE, constants.FEEDRATE)
        await self.grbl_connection.move(coordinates.x, coordinates.y, coordinates.z, constants.FEEDRATE)
        action()
        await self.grbl_connection.move(coordinates.x, coordinates.y, constants.CLERANCE, constants.FEEDRATE)
        action_after()

    async def move(self, position: GridPosition, height=0):
        """
        Moves the robot to a specified grid position.

        Args:
            position: The target grid position.
            height: The desired height (default: 0).
        """
        coordinates = self.grid.get_coordinates_from_grid(position)
        await self.grbl_connection.move(coordinates[0], coordinates[1], height, constants.FEEDRATE)

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
        await self.grbl_connection.send_command("G56")
        self.gripper.rotate(90)
        await self._move_and_act(self.grid.get_coordinates(obj), self._take_picture)
        self.gripper.rotate(0)
        await self.grbl_connection.send_command("G55")

    def _take_picture(self):
        """
        Private method to simulate taking a picture.
        """
        time.sleep(2)

    async def shutdown(self):
        """
        Shuts down the robot by moving to the home position and shutting down the gripper.
        """
        await self.grbl_connection.send_command("G54")
        await self.grbl_connection.move(0.0, 0.0, 0.0, constants.FEEDRATE)
        self.gripper.shutdown()
