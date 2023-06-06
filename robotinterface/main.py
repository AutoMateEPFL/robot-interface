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
    grid = Grid(x_max=-800, x_dist=-120, y_max=-610, y_dist=-180, z_max=100, object_height=16)
    plate1 = Pickable("plate", 0, GridPosition(0, grid.y_num_interval, 0))
    robot = await Robot.build(grid)

    for i in range(0, grid.x_num_interval):
        await robot.move(GridPosition(i, grid.y_num_interval, 0))
        input("Press Enter to continue...")
    await robot.shutdown()


asyncio.run(main())
