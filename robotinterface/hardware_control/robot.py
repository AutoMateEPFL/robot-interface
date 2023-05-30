import json
from robotinterface.drivers.dynamixel.controller import Dynamixel
from robotinterface.drivers.grbl.controller import GrblDriver
import logging

log = logging.getLogger(__name__)


class Robot:
    @classmethod
    async def build(cls):
        grbl_connection = None
        dyna_connection = None
        camera_connection = None

        file_path = "hardware_control/FirmwareSettings/port-settings.json"  # replace this with your actual file path
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
                dyna_connection.begin_communication()
                # TODO: activate mode of motors

            elif setting["name"] == "grbl":
                grbl_connection = await GrblDriver.build(setting["port"], setting["bauderate"])
        return cls(grbl_connection, dyna_connection, camera_connection)

    def __init__(self, grbl_connection, dyna_connection, camera_connection):
        self.dyna_connection = dyna_connection
        self.grbl_connection = grbl_connection
        self.camera_connection = camera_connection

    def pick_plate(self, plate_id):
        pass

    def place_plate(self, plate_id, grid_position):
        pass

    def take_photo(self, plate_id):
        pass

    def move_to(self, position):
        pass
