import json
from robotinterface.drivers.dynamixel.controller import Dynamixel
from robotinterface.drivers.grbl.controller import GrblDriver
from robotinterface.logistics.grid import Grid, GridPosition
from robotinterface.logistics.pickable import Pickable
from robotinterface.hardware_control import constants
from robotinterface.hardware_control.gripper import Gripper
import logging

log = logging.getLogger(__name__)


class Robot:
    @classmethod
    async def build(cls, grid: Grid):
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
                for motor in setting['motors']:
                    id = motor["id"]
                    name = motor["name"]
                    match name:
                        case "grip":
                            id_gripper = id
                            dyna_connection.set_operating_mode("pwm", id_gripper)
                        case "rot":
                            id_rotation = id
                            dyna_connection.set_operating_mode("position", id_rotation)
                        case _:
                            log.error(f"Unknown motor name: {name}")
                dyna_connection.enable_torque("all")

                gripper = Gripper(dyna_connection, id_gripper, id_rotation, 0)

            elif setting["name"] == "grbl":
                grbl_connection = await GrblDriver.build(setting["port"], setting["bauderate"])

            ## TODO: set the correct corrdinate system centered a sthe first grid position

        return cls(grbl_connection, gripper, camera_connection, grid)

    def __init__(self, grbl_connection, gripper, camera_connection, grid):
        self.gripper = gripper
        self.grbl_connection = grbl_connection
        self.camera_connection = camera_connection
        self.grid = grid

    async def pick(self, object: Pickable):
        await self.move_to(object.position)
        self.gripper.close()
        pass

    async def place(self, position: GridPosition,  object: Pickable):
        await self.move_to(position)
        self.gripper.open()
        object.position = position
        pass

    async def move_to(self, position: GridPosition):
        cooridnates = self.grid.get_coordinates(position)
        await self.grbl_connection.move(cooridnates[0], cooridnates[1], cooridnates[2], constants.FEEDRATE)
        pass
