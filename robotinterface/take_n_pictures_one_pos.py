import os
import sys
import platform
import asyncio
from logistics.grid import Grid, GridPosition
from hardware_control.robot import Robot
import numpy as np
from hardware_control import constants
from logistics.non_pickable import PlateHolder
from logistics.pickable import *
import logging
from logistics.computer_vision_utils import take_n_pictures_of_one_pos
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

async def main() :
    grid = Grid(x_max=-800, x_dist=-199, y_max=-620, y_dist=-200)
    loop = asyncio.get_running_loop()
    executor = ThreadPoolExecutor(max_workers=2)

    robot = await Robot.build(grid)

    #first fill plateholder
    brand = 'VWR'
    number_plates = 9
    grid_pos = GridPosition(0, 0)
    grid.add_object([PlateHolder()], grid_pos)
    for _ in range(number_plates) :
        grid.add_object([SmallPetriBottom(brand=brand), SmallPetriTop(brand=brand)], grid_pos)

    #Take pictures and move plates
    await take_n_pictures_of_one_pos(grid, robot, number_plates=number_plates, grid_pos=grid_pos)

    await robot.shutdown()

asyncio.run(main())


