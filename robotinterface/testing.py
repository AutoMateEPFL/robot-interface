import logging
import asyncio

from robotinterface.hardware_control.robot import Robot

from robotinterface.logistics.grid import Grid, GridPosition
from robotinterface.logistics.pickable import Pickable

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S')


async def main():
    grid = Grid(x_max=-800, x_dist=-200, y_max=-610, y_dist=-120)
    robot = await Robot.build(grid)
    await robot.gripper.close()
    await robot.gripper.open()
    await robot.gripper.rotate(90)
    await robot.gripper.shutdown()

asyncio.run(main())
