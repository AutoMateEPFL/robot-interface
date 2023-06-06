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
    grid = Grid(x_max=-800, x_dist=-120, y_max=-610, y_dist=-180)
    holder = Pickable(name="holder", id=0, height=5)
    plate1 = Pickable(name="plate1", id=0, height=21)
    plate2 = Pickable(name="plate1", id=1, height=21)
    plate3 = Pickable(name="plate1", id=1, height=21)
    plate4 = Pickable(name="plate1", id=1, height=21)
    plate5 = Pickable(name="plate1", id=1, height=21)

    grid.add_object(holder, GridPosition(0, grid.y_num_interval-1))
    grid.add_object(plate1, GridPosition(0, grid.y_num_interval-1))
    grid.add_object(plate2, GridPosition(0, grid.y_num_interval-1))
    grid.add_object(plate3, GridPosition(0, grid.y_num_interval - 1))
    grid.add_object(plate4, GridPosition(0, grid.y_num_interval - 1))
    grid.add_object(plate5, GridPosition(0, grid.y_num_interval - 1))


    robot = await Robot.build(grid)
    await robot.pick_and_place(plate5, GridPosition(2, grid.y_num_interval-1))
    await robot.pick_and_place(plate4, GridPosition(2, grid.y_num_interval-1))
    await robot.shutdown()

asyncio.run(main())
