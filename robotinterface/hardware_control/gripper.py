from robotinterface.drivers.dynamixel.controller import Dynamixel
from robotinterface.hardware_control import constants

import logging
import asyncio

log = logging.getLogger(__name__)


class Gripper:
    """
    This class represents the gripper of the robot. The gripper has the option to rotate around one axis

    Args:
                self.id_gripper: The id of the dynamixel for gripping
                self.id_rotation: The id of the dynamixel for rotating
                sefl.zero_position_rotation: The zero position of the rotation dynamixel

    """

    @classmethod
    async def build(cls, setting: dict[str, any]):
        """
        Asynchronously builds a Gripper instance.

        Args:
            dynamixel: The dynamixel object representing the workspace of the robot.
            id_gripper: The id of the dynamixel for gripping
            id_rotation: The id of the dynamixel for rotating
            zero_position_rotation: The zero position of the rotation dynamixel

        Returns:
            Gripper: The built Gripper instance.
        """
        ids = []
        for motor in setting['motors']:
            ids.append(motor['id'])
        ids.sort()

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
                case "rot":
                    id_rotation = id
                    zero = motor["zero_pos"]
                case _:
                    log.error(f"Unknown motor name: {name}")

        dynamixel = Dynamixel(ids, setting["port"], setting["bauderate"],
                                         ['xl' for _ in range(len(ids))])


        await dynamixel.set_operating_mode("pwm", id_gripper)
        await dynamixel.set_operating_mode("position", id_rotation)

        gripper = cls(dynamixel, id_gripper, id_rotation, zero)

        await gripper.open()
        await gripper.rotate(0)
        return gripper

    def __init__(self, dynamixel: Dynamixel, id_gripper: int, id_rotation: int, zero_position_rotation: int) -> None:
        """
        Initializes a gripper object

        Args:
            self.dynamixel: The connection to the dynamixel controller
            self.id_gripper: The id of the dynamixel for gripping
            self.id_rotation: The id of the dynamixel for rotating
            sefl.zero_position_rotation: The zero position of the rotation dynamixel
        """
        self.dynamixel = dynamixel
        self.id_gripper = id_gripper
        self.id_rotation = id_rotation
        self.zero_pos = zero_position_rotation

    @staticmethod
    def __degree_to_dynamixel(angle: float) -> int:
        """Translates degree to the the range 0 - 4095 used by the dynamixel
        
        Args:
            angle: The angle in degree to translate

        Returns:
            The discretized angle for the dynamixel
        """
        return int(angle * constants.ratio)

    async def rotate(self, angle: float) -> None:
        if self.id_rotation is None:
            raise ValueError("No rotation dynamixel connected")

        dyna_angle = self.__degree_to_dynamixel(angle)
        await self.dynamixel.write_position(
            self.zero_pos + dyna_angle, self.id_rotation)
        return

    async def close(self) -> None:
        "closes the gripper with a fixed current"
        await self.dynamixel.enable_torque("all")
        await self.dynamixel.write_pwm(constants.pwm_max, self.id_gripper)
        await asyncio.sleep(constants.closing_time)
        await self.dynamixel.write_pwm(constants.pwm, self.id_gripper)
        return

    async def open(self) -> None:
        "opens the gripper with a fixed current"
        await self.dynamixel.write_pwm(-constants.pwm_max, self.id_gripper)
        await asyncio.sleep(constants.opening_time)
        await self.dynamixel.write_pwm(-constants.pwm, self.id_gripper)
        return

    async def shutdown(self) -> None:
        "Disables the Torque for all motors"
        await self.dynamixel.disable_torque("all")
        return
