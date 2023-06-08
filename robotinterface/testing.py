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
    bottom = Pickable(name="bottom petri", id=0, height=12)
    top = Pickable(name="bottom petri", id=0, height=9)





    robot = await Robot.build(grid)
    for i in range(0, 1):
        await robot.move(GridPosition(i, grid.y_num_interval - 1))
        input("Press Enter to continue...")
    await robot.shutdown()

asyncio.run(main())
