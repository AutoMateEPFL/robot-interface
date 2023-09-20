from hardware_control.drivers.dynamixel.controller import Dynamixel
import hardware_control.constants
from hardware_control.drivers.serial.serial_port_detection import get_com_port

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
        logging.info("Building Gripper")
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
                    
        if setting["port"] == "auto":
            port = get_com_port("0403", "6014")
        else:
            port = setting["port"]

        dynamixel = await Dynamixel.build(ids, port, setting["bauderate"],
                                         ['xl' for _ in range(len(ids))])


        await dynamixel.set_operating_mode("pwm", id_gripper)
        await dynamixel.set_operating_mode("position", id_rotation)

        gripper = cls(dynamixel, id_gripper, id_rotation, zero)
        await gripper.dynamixel.enable_torque("all")

        await gripper.open()
        await gripper.rotate(0)
        logging.info("Gripper built")
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
        """Rotates the gripper around the z-axis"""
        logging.info(f"Rotating gripper to {angle} degree")
        if self.id_rotation is None:
            raise ValueError("No rotation dynamixel connected")

        dyna_angle = self.__degree_to_dynamixel(angle)
        await self.dynamixel.write_position(
            self.zero_pos + dyna_angle, self.id_rotation)
        return

    async def close(self) -> None:
        "closes the gripper with a fixed current"
        logging.info("Closing gripper")
        await self.dynamixel.enable_torque("all")
        await self.dynamixel.write_pwm(-constants.PWM_MAX, self.id_gripper)
        await self.position_smaller_than(constants.POSITION_CLOSE_TO_PD)
        await self.dynamixel.write_pwm(-constants.PWM_SOFT, self.id_gripper)
        await self.object_reached()
        await self.dynamixel.write_pwm(-constants.PWM_RETAIN, self.id_gripper)
        
        # await asyncio.sleep(constants.closing_time)
        # await self.dynamixel.write_pwm(-constants.pwm, self.id_gripper)
        return

    async def open(self) -> None:
        "opens the gripper with a fixed current"
        logging.info("Opening gripper")
        await self.dynamixel.write_pwm(constants.PWM_MAX, self.id_gripper)
        await self.position_greater_than(constants.POSITION_OPEN)
        await self.dynamixel.write_pwm(constants.PWM_RETAIN, self.id_gripper)
        return

    async def shutdown(self) -> None:
        "Disables the Torque for all motors"
        logging.info("Shutting down gripper")
        await self.dynamixel.disable_torque("all")
        return
            
    async def position_greater_than(self, limit) -> None:
        "Checks if the gripper as reached a position greater than the limit"
        start_time = asyncio.get_event_loop().time()
                
        while True:
            real_position = await self.dynamixel.read_position(self.id_gripper)
            if real_position > limit:
                return 
            
            elapsed_time = asyncio.get_event_loop().time() - start_time
            if elapsed_time > constants.TIMEOUT_POSITION_REACHED:
                raise TimeoutError("Time limit exceeded while waiting for the position to be reached.")
            
            await asyncio.sleep(0.01)
            
    async def position_smaller_than(self, limit) -> None:
        "Checks if the gripper as reached a position smaller than the limit"
        start_time = asyncio.get_event_loop().time()
                
        while True:
            real_position = await self.dynamixel.read_position(self.id_gripper)
            if real_position < limit:
                return 
            
            elapsed_time = asyncio.get_event_loop().time() - start_time
            if elapsed_time > constants.TIMEOUT_POSITION_REACHED:
                raise TimeoutError("Time limit exceeded while waiting for the position to be reached.")
            
            await asyncio.sleep(0.01)

    async def object_reached(self) -> None:
        "Checks if the gripper has an object"
        start_time = asyncio.get_event_loop().time()
        
        while True:
            real_current = await self.dynamixel.read_current(self.id_gripper)
            if abs(real_current) > constants.CURRENT_VIRTUAL_ENDSTOP:
                return
            
            elapsed_time = asyncio.get_event_loop().time() - start_time
            if elapsed_time > constants.TIMEOUT_OBJECT_REACHED:
                raise TimeoutError("Time limit exceeded while waiting for the object to be reached.")
            
            await asyncio.sleep(0.01)
            
    # async def diameter_to_position(self, diameter: float) -> float:
    #     """Translates a diameter to a position for the gripper
        
    #     Args:
    #         diameter: The diameter of the object to grip

    #     Returns:
    #         The position for the gripper
    #     """
    #     diameter_range = constants.DIAMETER_OPEN-constants.DIAMETER_CLOSED
    #     position_range = constants.POSITION_OPEN-constants.POSITION_CLOSED
    
    #     return int((diameter-constants.DIAMETER_CLOSED)/diameter_range*position_range)+constants.POSITION_CLOSED
