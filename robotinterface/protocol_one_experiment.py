# Interpreter path
# C:\Users\APrap\AppData\Local\pypoetry\Cache\virtualenvs\robotinterface-u1VIN2jz-py3.10

import os
import sys
import platform
if platform.system() == 'Windows':
    sys.path.append(os.path.join(sys.path[0],'..'))
else:
    sys.path.append(r"/Users/Etienne/Documents/GitHub/robot-interface")
import logging
import asyncio

from job_library import *
from robotinterface.hardware_control.robot import Robot

from robotinterface.logistics.grid import Grid, GridPosition
from robotinterface.logistics.pickable import *
from robotinterface.gui.user_gui import load_grid
from concurrent.futures import ThreadPoolExecutor
from functools import partial

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')


async def main():
    grid = Grid(x_max=-800, x_dist=-199, y_max=-620, y_dist=-200)
    grid.set_camera_and_stack_position(GridPosition(2, 1), GridPosition(3, 1) )
    
    stack_pos = grid.find_object(grid.stack)
    pic_pos = grid.find_object(grid.cam)
    
    loop = asyncio.get_running_loop()
    executor = ThreadPoolExecutor(max_workers=2)
    
    #robot = await Robot.build(grid)

    grid = load_grid(grid)

    take_photo_of_all_experiments_and_reconstruct_piles(robot, grid, pic_pos, stack_pos)


asyncio.run(main())
