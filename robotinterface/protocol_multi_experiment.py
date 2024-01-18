# Interpreter path
# C:\Users\APrap\AppData\Local\pypoetry\Cache\virtualenvs\robotinterface-u1VIN2jz-py3.10

import os
import sys
import platform
from experiment_helper import *
if platform.system() == 'Windows':
    sys.path.append(os.path.join(sys.path[0], '..'))
else:
    #sys.path.append(r"/Users/AutoMate EPFL/Documents/GitHub/robot-interface")
    sys.path.append(os.path.join(sys.path[0], '..'))
import logging
import asyncio
from robotinterface.hardware_control.robot import Robot
from robotinterface.logistics.grid import Grid, GridPosition
from robotinterface.gui.user_gui import load_grid
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

async def main():
    # Def grid :
    grid = Grid(x_max=-800, x_dist=-199, y_max=-620, y_dist=-200)

    grid.set_camera_position(GridPosition(2, 1))
    grid.set_stack_positions([GridPosition(3, i) for i in range(0,4)]+[GridPosition(4, i) for i in range(0,4)])
    # Camera position will be uesed as the ick and place position:
    pic_pos = grid.find_object(grid.cam)

    # async loop:
    loop = asyncio.get_running_loop()
    executor = ThreadPoolExecutor(max_workers=2)
    if platform.system() == 'Windows':
        robot = await Robot.build(grid)

    #load_csv_of_experiments(grid,path="AutoMate_panel.csv")
    grid = load_grid(grid)

    list_of_piles = find_all_PlateHolder(grid)
    reconstruct_pile = False
    is_it_first_picture = True

    # FOR EACH EXPERIMENT TAKE PICTURES AND DECONSTRUCT THE PILE
    for index, plate_holder in enumerate(list_of_piles):
        stack_pos = grid.find_object(grid.stack_list[index])
        #save_datalog_of_a_plateholder(plate_holder)
        pos_experiment = grid.find_object(plate_holder)
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

            await robot.take_picture(target[0], obj_rem=target[1], folder_name=target[0]._associated_experiment,
                                        prefix="marker_" + str(target[0].number) + "_",
                                        suffix="_" + str(target[0].associated_name), to_save = True, pic_pos=pic_pos)

            # Place all petri dishes on the stack pos, except last one
            #If the pile has to be reconstructed, directly put the last one on its initial pos
            if num != n_petri - 1:
                await robot.pick_and_place(target, stack_pos)
            else:
                if reconstruct_pile:
                    await robot.pick_and_place(target, pos_experiment)
                else:
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
