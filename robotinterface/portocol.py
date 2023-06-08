import logging
import asyncio

from robotinterface.hardware_control.robot import Robot

from robotinterface.logistics.grid import Grid, GridPosition
from robotinterface.logistics.pickable import *

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S')


async def main():
    grid = Grid(x_max=-800, x_dist=-200, y_max=-610, y_dist=-120)

    zero_pos = GridPosition(0, 0)
    holder = PlateHolder
    bottom1 = SmallPetriBottom()
    top1 = SmallPetriTop()
    bottom2 = SmallPetriBottom()
    top2 = SmallPetriTop()
    bottom3 = SmallPetriBottom()
    top3 = SmallPetriTop()
    bottom4 = SmallPetriBottom()
    top4 = SmallPetriTop()
    grid.add_object([holder,
                     bottom1, top1,
                     bottom2, top2,
                     bottom3, top3,
                     bottom4, top4,
                     ], zero_pos)


    robot = await Robot.build(grid)
    await robot.pick_and_place([bottom4, top4],
                               GridPosition(1, 0))
    await robot.pick_and_place([top4], GridPosition(2, 0))
    await robot.take_picture(bottom4)
    await robot.pick_and_place([top4], GridPosition(1, 0))
    await robot.pick_and_place([bottom4, top4],
                               GridPosition(0, 0))
    await robot.shutdown()


asyncio.run(main())
