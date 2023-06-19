import logging
import asyncio

from robotinterface.hardware_control.robot import Robot

from robotinterface.logistics.grid import Grid, GridPosition
from robotinterface.logistics.pickable import Pickable, SmallPetriBottom

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')


async def main():
    grid = Grid(x_max=-800, x_dist=-200, y_max=-610, y_dist=-120)
    bottom1 = SmallPetriBottom()
    grid.add_object([bottom1], GridPosition(0, 0))
    robot = await Robot.build(grid)
    await robot.save_picture(bottom1)
    await robot.pick_and_place([bottom1], GridPosition(1, 1))
    await robot.shutdown()

asyncio.run(main())
