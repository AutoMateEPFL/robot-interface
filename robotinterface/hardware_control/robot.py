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
                id_gripper = None
                id_rotation = None
                zero = None

                for motor in setting['motors']:
                    id = motor["id"]
                    name = motor["name"]
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
                dyna_connection.enable_torque("all")

                gripper = Gripper(dyna_connection, id_gripper, id_rotation, zero)
                gripper.open()
                #gripper.rotate(0)

            elif setting["name"] == "grbl":
                grbl_connection = await GrblDriver.build(setting["port"], setting["bauderate"])
                await grbl_connection.home()
                await grbl_connection.send_command(f"G10 L2 P2 X0 Y0 Z{constants.Z_OFFSET}")
                await grbl_connection.send_command("G55")

        return cls(grbl_connection, gripper, camera_connection, grid)

    def __init__(self, grbl_connection, gripper, camera_connection, grid):
        self.gripper = gripper
        self.grbl_connection = grbl_connection
        self.camera_connection = camera_connection
        self.grid = grid

    async def _move_and_act(self, position, action, action_after=lambda: None):
        coordinates = self.grid.get_coordinates(position)
        await self.grbl_connection.move(coordinates[0], coordinates[1], constants.CLERANCE, constants.FEEDRATE)
        await self.grbl_connection.move(coordinates[0], coordinates[1], coordinates[2], constants.FEEDRATE)
        action()
        await self.grbl_connection.move(coordinates[0], coordinates[1], constants.CLERANCE, constants.FEEDRATE)
        action_after()

    async def move(self, position: GridPosition):
        coordinates = self.grid.get_coordinates(position)
        await self.grbl_connection.move(coordinates[0], coordinates[1], coordinates[2], constants.FEEDRATE)

    async def pick(self, object: Pickable):
        await self._move_and_act(object.position, self.gripper.close)

    async def place(self, position: GridPosition, object: Pickable):
        await self._move_and_act(position, self.gripper.open, lambda: setattr(object, 'position', position))

    async def pick_and_place(self, position: GridPosition, object: Pickable):
        await self._move_and_act(object.position, self.gripper.close)
        await self._move_and_act(position, self.gripper.open, lambda: setattr(object, 'position', position))

    async def shutdown(self):
        await self.grbl_connection.send_command("G54")
        await self.grbl_connection.move(0, 0, 0, constants.FEEDRATE)
