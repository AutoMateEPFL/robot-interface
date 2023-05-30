import logging
import asyncio

from robotinterface.hardware_control.robot import Robot

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S')


async def main():
    robot = await Robot.build()
    await robot.grbl_connection.home()

asyncio.run(main())
