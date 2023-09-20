# poetry run python robotinterface\protocol.py
# Interpreter path
# C:\Users\APrap\AppData\Local\pypoetry\Cache\virtualenvs\robotinterface-u1VIN2jz-py3.10

import os
import sys 
sys.path.append(os.path.join(sys.path[0],'..'))

import logging
import asyncio

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
    
    drop_pos = GridPosition(grid.x_num_interval-1, grid.y_num_interval-1)
    pic_pos = GridPosition(2, 2)
    
    loop = asyncio.get_running_loop()
    executor = ThreadPoolExecutor(max_workers=2)
    
    robot = await Robot.build(grid)

    grid = await loop.run_in_executor(executor, partial(load_grid, grid))
    
    # TO DO : add a function to realize the protocol, check the load_grid function maybe find a better way to rewrite it in asyncronous way 
    for x in range(grid.x_num_interval):
        for y in range(grid.y_num_interval):
            for num in range(len(grid.object_grid[y][x])-1):
                object = grid.object_grid[y][x][num]
                next_object = grid.object_grid[y][x][num+1]
                if object.name == "Small Petri Bottom":
                    if next_object.name == "Small Petri Top":
                         target = [object, next_object]
                    else:
                        target = [object]

    await robot.pick_and_place(target, pic_pos)
    await robot.take_picture(target[0], obj_rem=target[1])
    await robot.pick_and_place(target, drop_pos)
    
    await robot.shutdown()


asyncio.run(main())
