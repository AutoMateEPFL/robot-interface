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
    grid = Grid(-200, 10, -200, 10, -100, 5)
    plate = Pickable("plate", 0, GridPosition(3, 3, 3), 5)
    robot = await Robot.build(grid)
    await robot.grbl_connection.home()
    await robot.pick(plate)
    await robot.place(GridPosition(0, 0, 0), plate)







asyncio.run(main())
