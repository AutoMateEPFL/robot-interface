# Interpreter path
# C:\Users\APrap\AppData\Local\pypoetry\Cache\virtualenvs\robotinterface-u1VIN2jz-py3.10

import os
import sys
import platform
from job_library import *
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
    grid.set_camera_and_stack_position(GridPosition(2, 1), GridPosition(3, 1) )
    
    stack_pos = grid.find_object(grid.stack)
    pic_pos = grid.find_object(grid.cam)
    
    loop = asyncio.get_running_loop()
    executor = ThreadPoolExecutor(max_workers=2)
    
    robot = await Robot.build(grid)

    grid = load_grid(grid)

    list_of_experiments = find_all_experiments(grid)
    ## to do function to load experiment

    reconstruct_pile = False

    # FOR EACH EXPERIMENT TAKE PICTURES AND DECONSTRUCT THE PILE

    for experiment in list_of_experiments:
        pos_experiment = grid.find_object(experiment)
        x_exp, y_exp = pos_experiment.x_id, pos_experiment.y_id
        n_petri = (len(grid.object_grid[y_exp][x_exp]) - 1) // 2
        print("n petri", n_petri)
        print(grid.object_grid[y_exp][x_exp])
        for num in range(n_petri):
            object = grid.object_grid[y_exp][x_exp][-2]
            next_object = grid.object_grid[y_exp][x_exp][-1]
            if object.name == "Small Petri Bottom":
                if next_object.name == "Small Petri Top":
                    target = [object, next_object]
                else:
                    target = [object]

            await robot.pick_and_place(target, pic_pos)

            await robot.take_picture(target[0], obj_rem=target[1], folder_name=experiment.associated_name, suffix="_"+str(target[0].associated_name))
            await robot.pick_and_place(target, stack_pos)

        if reconstruct_pile:
            # RECONSTRUCT THE PILE ON THE INITIAL POS
            x_stack, y_stack = stack_pos.x_id, stack_pos.y_id
            for num in range(len(grid.object_grid[y_stack][x_stack]) // 2):
                object = grid.object_grid[y_stack][x_stack][-2]
                next_object = grid.object_grid[y_stack][x_stack][-1]
                if object.name == "Small Petri Bottom":
                    if next_object.name == "Small Petri Top":
                        target = [object, next_object]
                    else:
                        target = [object]
                await robot.pick_and_place(target, pos_experiment)

    await robot.shutdown()


asyncio.run(main())
