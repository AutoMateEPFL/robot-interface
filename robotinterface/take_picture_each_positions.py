import os
import sys
import platform
from experiment_helper import *
if platform.system() == 'Windows':
    sys.path.append(os.path.join(sys.path[0], '..'))

import logging
import asyncio
from hardware_control.robot import Robot
from logistics.grid import Grid, GridPosition
from logistics.grid_utils import fill_grid, get_plateholder_petri_pos, fill_all
from gui.gui import InteractiveWindow
from logistics.computer_vision_utils import take_picture_of_all_postitions
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')



async def main() :
    grid = Grid(x_max=-800, x_dist=-199, y_max=-620, y_dist=-200)
    loop = asyncio.get_running_loop()
    executor = ThreadPoolExecutor(max_workers=2)

    # Robot build
    if platform.system() == 'Windows':
        robot = await Robot.build(grid)

    # fill_all(grid)
    #  take picture of all positions
    await take_picture_of_all_postitions(grid, robot, number_plateholder=8)

    await robot.shutdown()

asyncio.run(main())