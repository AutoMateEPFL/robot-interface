import json
import time
import types
import asyncio
import os
from logistics.grid import Grid
from logistics.positions import GridPosition, CartesianPosition
from logistics.pickable import Pickable
import platform
my_platform = platform.system()
if my_platform == 'Windows':
    from hardware_control import constants
else :
    import hardware_control.constants
from hardware_control.gripper import Gripper
from hardware_control.platform_robot import Platform
from hardware_control.vision import Vision
import logging
import platform

my_platform = platform.system()

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


        SECRET_KEY = os.environ.get('AM_I_IN_A_DOCKER_CONTAINER', False)

        # Load the settings from the json file
        if SECRET_KEY:
            file_path = "hardware_control/FirmwareSettings/Docker.json"
        
        if my_platform == 'Windows':
            file_path = "robotinterface/hardware_control/FirmwareSettings/windows.json"
        else:
            file_path = "/Users/Etienne/Documents/GitHub/robot-interface/robotinterface/hardware_control/FirmwareSettings/mac.json"
        with open(file_path, 'r') as f:
            data = json.load(f)
            
        #  Load the tools settings from the json file
        if my_platform == 'Windows':
            file_path = "robotinterface/hardware_control/FirmwareSettings/tools_configuration.json"
        else:
            file_path = "/Users/Etienne/Documents/GitHub/robot-interface/robotinterface/hardware_control/FirmwareSettings/tools_configuration.json"

            
        #file_path = "/Users/Etienne/Documents/GitHub/robot-interface/robotinterface/hardware_control/FirmwareSettings/tools_configuration.json"
        with open(file_path, 'r') as f:
            tools_settings = json.load(f)
            
        tools_list = {}
        for tool in tools_settings["Tools"]:
            tools_list[tool["name"]] = tool["id"]

        gripper_task = None
        platform_task = None
        camera_connection_task = None
        for setting in data["ComSettings"]:
            if setting["name"] == "dyna":
                gripper_task = asyncio.create_task(Gripper.build(setting))
            elif setting["name"] == "grbl":
                platform_task = asyncio.create_task(Platform.build(setting, tools_settings["Tools"]))
            elif setting["name"] == "camera":
                camera_connection_task = asyncio.create_task(Vision.build(setting))

        # Initialize the tasks to None
        gripper, platform, camera = None, None, None

        # Collect all available tasks
        tasks = [(task, name) for task, name in ((gripper_task, 'gripper'),
                                                 (platform_task, 'platform'),
                                                 (camera_connection_task, 'camera')) if task]

        # If there are tasks to perform
        if tasks:
            # Perform all available tasks in parallel
            results = await asyncio.gather(*(task for task, _ in tasks))

            # Assign the results to the corresponding variables
            for (task, name), result in zip(tasks, results):
                if name == 'gripper':
                    gripper = result
                elif name == 'platform':
                    platform = result
                elif name == 'camera':
                    camera = result

        return cls(platform, gripper, camera, grid, tools_list)

    def __init__(self, platform: Platform, gripper: Gripper, camera: Vision, grid: Grid, tools_list: dict[str, int]):
        """
        Initializes a new instance of the Robot class.

        Args:
            platform: The connection to the GRBL controller.
            gripper: The gripper of the robot.
            camera: The connection to the camera (if any).
            grid: The grid object representing the workspace of the robot.
            tools_list: The list of tools available to the robot.
        """
        self.gripper = gripper
        self.platform = platform
        self.camera = camera
        self.grid = grid
        self.tools_list = tools_list
        self.robot_position = None

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
        
    
    async def _move_and_act_fast(self, coordinates: CartesianPosition, action: types.FunctionType, need_clearance: bool = True, action_after=lambda: None):
        """
        Moves the robot to the specified coordinates and performs an action.

        Args:
            coordinates: The target Cartesian coordinates.
            action: The action to perform at the target coordinates.
            action_after: The action to perform after returning to the clearance position (default: lambda: None).
        """
        logging.info(f"Moving to x:{coordinates.x}, y:{coordinates.y}, z:{coordinates.z}")
        
        if need_clearance:
            await self.platform.vertical_move(constants.CLERANCE, constants.FEEDRATE)
            await self.platform.move(coordinates.x, coordinates.y, constants.CLERANCE, constants.FEEDRATE)
            
        await self.platform.vertical_move(coordinates.z, constants.FEEDRATE)
        await action()
        action_after()
        
    async def change_tool(self, tool: str):
        """
        Changes the tool of the robot.

        Args:
            tool (str): The name of the tool to be changed to.
        """
        try:
            id = self.tools_list[tool]
            await self.platform.set_space(id)
        except KeyError:
            logging.debug(f"Tool {tool} not found")

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
        position = self.grid.find_object(objects[0])
        if self.robot_position != position:
            need_clearance = True
        else:
            need_clearance = False

        coordinates = self.grid.remove_object(objects)
        await self._move_and_act_fast(coordinates, self.gripper.close, need_clearance)
        self.robot_position = position

    async def place(self, objects: list[Pickable], position: GridPosition):
        """
        Places objects on the grid at a specified position.

        Args:
            objects: The objects to be placed.
            position: The target grid position.
        """
        if position != self.robot_position:
            need_clearance = True
        else:
            need_clearance = False
            
        coordinates = self.grid.add_object(objects, position)
        await self._move_and_act_fast(coordinates, self.gripper.open, need_clearance)
        self.robot_position = position

    async def pick_and_place(self, objects: list[Pickable], position: GridPosition):
        """
        Picks up objects and places them at a specified grid position.

        Args:
            objects: The objects to be picked up and placed.
            position: The target grid position.
        """
        await self.pick(objects)
        await self.place(objects, position)

    async def save_picture(self,folder_name="", prefix="",suffix="",to_save=True):
        """
        Save a picture.
        
        """
        await self.camera.save_picture(folder_name=folder_name, prefix=prefix, suffix=suffix, to_save=to_save)
        
        
    async def take_picture(self, obj: Pickable, obj_rem: Pickable = None, folder_name="", prefix="", suffix="",to_save=True, pic_pos=""):
        """
        Takes a picture of a specified object.

        Args:
            obj: The object to take a picture of.
        """
        if obj_rem is not None:
            await self.pick([obj_rem])
        
        coordinates = self.grid.get_coordinates(obj)
        await self.platform.vertical_move(constants.PETRI_CLERANCE, constants.FEEDRATE)
        await self.change_tool("camera")
        await self.gripper.rotate(90)
        await self.platform.move(coordinates.x, coordinates.y, constants.PICTURE_HEIGHT, constants.FEEDRATE)
        await self.save_picture(folder_name=folder_name,prefix=prefix, suffix=suffix,to_save=to_save)
        #await self.platform.move(pic_pos.x, pic_pos.y, constants.PICTURE_HEIGHT, constants.FEEDRATE)
        await self.gripper.rotate(0)
        await self.change_tool("gripper")
        await self.platform.move(coordinates.x, coordinates.y,  constants.PETRI_CLERANCE, constants.FEEDRATE)


        
        if obj_rem is not None:
            await self.place([obj_rem], self.robot_position)

    async def shutdown(self):
        """
        Shuts down the robot by moving to the home position and shutting down the gripper.
        """
        logging.info("Shutting down robot")
        await self.platform.vertical_move(constants.CLERANCE, constants.FEEDRATE)
        await self.platform.set_space(1)
        await self.platform.move(0.0, 0.0, 260, constants.FEEDRATE)
        await self.gripper.shutdown()
        await self.camera.shutdown()
