from robotinterface.drivers.grbl.communication import SerialConnection
from robotinterface.drivers.grbl import parser
from robotinterface.drivers.grbl.constants import System

import asyncio
import logging

log = logging.getLogger(__name__)

class GrblDriver:
    """
    Represents a driver for the GRBL controller.

    Attributes:
        _connection (SerialConnection): The serial connection to the GRBL controller.
    """

    @classmethod
    async def build(cls, port: str, bauderate: int):
        """
        Builds a GrblDriver instance.

        Args:
            port (str): The port to connect to.
            bauderate (int): The baud rate of the connection.

        Returns:
            GrblDriver: The built GrblDriver instance.
        """
        connection = await SerialConnection.create(port, bauderate)
        answer = await connection.send_bytes(System.RESET, True)
        parser.welcome_parser(answer)
        return cls(connection)

    def __init__(self, connection: SerialConnection):
        """
        Initializes a new instance of the GrblDriver class.

        Args:
            connection (SerialConnection): The serial connection to the GRBL controller.
        """
        self._connection = connection

    async def home(self):
        """
        Sends the home command to the GRBL controller and waits for homing to complete.

        Raises:
            ValueError: If there is a problem with homing or with communications
        """
        answer = await self._connection.send("$H")
        parser.homing_start_parser(answer)
        ack_homing_1 = await self._connection.get_answer()
        ack_homing_2 = await self._connection.get_answer()
        parser.homing_end_parser(ack_homing_1, ack_homing_2)

    async def _wait_till_idle(self) -> None:
        """
        Waits until the GRBL controller becomes idle.

        Raises:
            ValueError: If there is a error in communication
        """
        not_idle = True
        while not_idle:
            answer = await self._connection.send(System.STATUS)
            not_idle = not parser.idle_parser(answer)
            await asyncio.sleep(0.1)
        logging.debug("Robot is idle again")

    async def move(self, x: float, y: float, z: float, feedrate: int) -> None:
        """
        Moves the robot to the specified coordinates.

        Args:
            x: The X coordinate.
            y: The Y coordinate.
            z: The Z coordinate.
            feedrate: The feedrate.

        Raises:
            ValueError: If the move command fails.
        """
        answer = await self._connection.send(f"G01 X{x} Y{y} Z{z} F{feedrate}")
        parser.move_parser(answer)
        await self._wait_till_idle()

    async def send_command(self, command: str) -> None:
        """
        Sends a command to the GRBL controller.

        Args:
            command: The command to send.

        Raises:
            ValueError: If an error or alarm is received as a response.
        """
        answer = await self._connection.send(command)
        parser.handle_error_alarm(answer)

if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.DEBUG,
        datefmt='%Y-%m-%d %H:%M:%S')

    async def main():
        grbl_driver = await GrblDriver.build("COM7", 115200)
        await grbl_driver.home()
        await grbl_driver.move(-500, -500, 4000)
    asyncio.run(main())
