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
    grid.set_camera_and_stack_position(GridPosition(4, 3), GridPosition(3, 3) )
    
    stack_pos = grid.find_object(grid.stack)
    pic_pos = grid.find_object(grid.cam)
    
    loop = asyncio.get_running_loop()
    executor = ThreadPoolExecutor(max_workers=2)
    
    #robot = await Robot.build(grid)

    #grid = await loop.run_in_executor(executor, partial(load_grid, grid))
    grid = load_grid(grid)

# FIND ALL EXPERIMENTS IN THE GRID, FOR NOW ONE EXPERIMENT = ONE PLATEHOLDER
    list_of_experiments = []
    for x in range(grid.x_num_interval):
        for y in range(grid.y_num_interval):
            if grid.object_grid[y][x] != [] :
                print('grid', grid.object_grid[y][x][0])
                print(str(type(grid.object_grid[y][x][0]))=="<class 'logistics.pickable.PlateHolder'>")
                if str(type(grid.object_grid[y][x][0]))=="<class 'logistics.pickable.PlateHolder'>" :
                    print('EXPERIMENT FOUND',x,y)
                    list_of_experiments.append(grid.object_grid[y][x][0])

# FOR EACH EXPERIMENT TAKE PICTURES AND DECONSTRUCT THE PILE
    for experiment in list_of_experiments:
        pos_experiment = grid.find_object(experiment)
        x_exp, y_exp = pos_experiment.x_id, pos_experiment.y_id
        n_petri = len(grid.object_grid[y_exp][x_exp])-1
        for num in range(n_petri):
            object = grid.object_grid[y_exp][x_exp][num]
            next_object = grid.object_grid[y_exp][x_exp][num + 1]
            if object.name == "Small Petri Bottom":
                if next_object.name == "Small Petri Top":
                    target = [object, next_object]
                else:
                    target = [object]


            await robot.pick_and_place(target, pic_pos)

            await robot.take_picture(target[0], obj_rem=target[1])
            await robot.pick_and_place(target, stack_pos)
# RECONSTRUCT THE PILE ON THE INITIAL POS
        x_stack, y_stack = stack_pos.x, stack_pos.y
        for num in range(len(grid.object_grid[y_stack][x_stack]) - 1):
            object = grid.object_grid[y_stack][x_stack][num]
            next_object = grid.object_grid[y_stack][x_stack][num + 1]
            if object.name == "Small Petri Bottom":
                if next_object.name == "Small Petri Top":
                    target = [object, next_object]
                else:
                    target = [object]

            await robot.pick_and_place(target, pos_experiment)



    # TO DO : add a function to realize the protocol, check the load_grid function maybe find a better way to rewrite it in asyncronous way 
    # for x in range(grid.x_num_interval):
    #     for y in range(grid.y_num_interval):
    #         for num in range(len(grid.object_grid[y][x])-1):
    #             object = grid.object_grid[y][x][num]
    #             next_object = grid.object_grid[y][x][num+1]
    #             if object.name == "Small Petri Bottom":
    #                 if next_object.name == "Small Petri Top":
    #                      target = [object, next_object]
    #                 else:
    #                     target = [object]


    
    await robot.shutdown()


asyncio.run(main())
