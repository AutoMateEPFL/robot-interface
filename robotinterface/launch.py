import os
import sys
import platform
from experiment_helper import *
if platform.system() == 'Windows':
    sys.path.append(os.path.join(sys.path[0], '..'))

import logging
import asyncio
from robotinterface.hardware_control.robot import Robot
from robotinterface.logistics.grid import Grid, GridPosition
from robotinterface.logistics.grid_utils import fill_grid
from robotinterface.gui.new_interface import InteractiveWindow
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')


async def main():
    # Def grid :
    grid = Grid(x_max=-800, x_dist=-199, y_max=-620, y_dist=-200)

    # Camera position will be used as the pick and place position:
    camera_pos = GridPosition(2, 1)
    grid.set_camera_position(camera_pos)

    # Set the stacks positions
    grid.set_stack_positions([GridPosition(3, i) for i in range(0,4)]+[GridPosition(4, i) for i in range(0,4)])

    # Launch the gui and get the data
    experiment_window = InteractiveWindow(title = 'Experiment Window')
    experiment_data = experiment_window.get_experiment_data()

    # Fill the grid according to the data
    fill_grid(grid, experiment_data)

    # async loop:
    loop = asyncio.get_running_loop()
    executor = ThreadPoolExecutor(max_workers=2)
    # if platform.system() == 'Windows':
    #     robot = await Robot.build(grid)


asyncio.run(main())
    
