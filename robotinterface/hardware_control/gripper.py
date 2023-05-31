from robotinterface.drivers.dynamixel.controller import Dynamixel
from robotinterface.hardware_control import constants

import logging
import time

log = logging.getLogger(__name__)


class Gripper:
    """
    Encapsulating acutation of a gripper. The gripper has dynamixel motor for rotation and one for gripping.

    Attributes:
        self.pwm: Is the speed the grippers use to be opened or closed

    """

    def __init__(self, dynamixel: Dynamixel, id_gripper: int, id_rotation: int, zero_position_rotation: int) -> None:
        """
        Initializing with the diffrent dynamixels and the zero position for rotation

        Args:
            self.id_gripper: The dynamixel for gripping
            self.id_rotation: The dynamixel for rotating
            sefl.zero_position_rotation: The zero position of the rotation dynamixel
        """
        self.dynamixel = dynamixel
        self.id_gripper = id_gripper
        self.id_rotation = id_rotation
        self.zero_pos = zero_position_rotation

    @staticmethod
    def __degree_to_dynamixel(self, angle: float) -> float:
        """Translates degree to the angle measurment dynamixels use"""
        return angle * constants.ratio

    def rotate(self, angle: float) -> None:
        dyna_angle = self.__degree_to_dynamixel(angle)
        print(angle)
        self.dynamixel.write_position(
            self.zero_pos + dyna_angle, self.id_rotation)
        print(self.zero_pos + dyna_angle)
        return

    def close(self) -> None:
        "closes the gripper with a fixed current"
        self.dynamixel.write_pwm(constants.pwm_max, self.id_gripper)
        time.sleep(constants.closing_time)
        self.dynamixel.write_pwm(constants.pwm, self.id_gripper)
        return

    def open(self) -> None:
        "opens the gripper with a fixed current"
        self.dynamixel.write_pwm(-constants.pwm_max, self.id_gripper)
        time.sleep(constants.opening_time)
        self.dynamixel.write_pwm(-constants.pwm, self.id_gripper)
        return

