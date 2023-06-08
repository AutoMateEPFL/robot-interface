from robotinterface.drivers.grbl.communication import SerialConnection
from robotinterface.drivers.grbl import parser
from robotinterface.drivers.grbl.constants import (
    System
)

import asyncio
import logging

log = logging.getLogger(__name__)

class GrblDriver:
    @classmethod
    async def build(cls, port: str, bauderate: int):
        connection = await SerialConnection.create(port, bauderate)
        answer = await connection.send_bytes(System.RESET, True)

        tries = 0
        while True:
            try:
                parser.welcome_parser(answer)
                break  # If the code block executed successfully, break the loop.
            except Exception as e:
                print(f"An error occurred: {e}")
                answer = await connection.send_bytes(System.RESET, True)
                parser.welcome_parser(answer)
                tries += 1
                if tries > 10:
                    raise e
                pass  # If the code block failed, ignore the error and repeat the loop.

        return cls(connection)

    def __init__(self, connection: SerialConnection):
        self._connection = connection

    async def home(self):
        #try homing again even if it fails the first time. There is a communication error sometimes

        answer = await self._connection.send("$H")
        parser.homing_start_parser(answer)
        ack_homing_1 = await self._connection.get_answer()
        ack_homing_2 = await self._connection.get_answer()
        parser.homing_end_parser(ack_homing_1, ack_homing_2)
        return


    async def _wait_till_idle(self) -> None:
        not_idle = True
        while not_idle:
            answer = await self._connection.send(System.STATUS)
            not_idle = not parser.idle_parser(answer)
            await asyncio.sleep(0.1)
        logging.debug("Robot is idle again")
        return

    async def move(self, x: float, y: float, z:float, feedrate: int) -> None:
        answer = await self._connection.send(f"G01 X{x} Y{y} Z{z} F{feedrate}")
        parser.move_parser(answer)
        await self._wait_till_idle()
        return

    async def send_command(self, command: str) -> None:
        answer = await self._connection.send(command)
        #parser.move_parser(answer)
        return


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




