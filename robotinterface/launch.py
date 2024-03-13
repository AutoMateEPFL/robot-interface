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
from robotinterface.logistics.grid_utils import fill_grid, get_plateholder_petri_pos
from robotinterface.gui.gui import InteractiveWindow
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')


async def main():
    # Def grid :
    grid = Grid(x_max=-800, x_dist=-199, y_max=-620, y_dist=-200)

    # Camera position will be used as the pick and place position:
    pic_pos = GridPosition(2, 1)
    grid.set_camera_position(pic_pos)

    # Set the stacks positions
    grid.set_stack_positions([GridPosition(3, i) for i in range(0,4)]+[GridPosition(4, i) for i in range(0,4)])

    # async loop:
    loop = asyncio.get_running_loop()
    executor = ThreadPoolExecutor(max_workers=2)

    # Robot build
    # if platform.system() == 'Windows':
    #     robot = await Robot.build(grid)

    # Launch the gui and get the data
    experiment_window = InteractiveWindow(title = 'Experiment Window')
    experiment_data = experiment_window.get_experiment_data()

    # Fill the grid according to the data
    fill_grid(grid, experiment_data)

    # Get the plateholder positions and number of petri dishes
    plateholder_petri_pos = get_plateholder_petri_pos(grid)
    total_plateholders = len(plateholder_petri_pos)

    # Move to camera pos, take picture and move to stack pos
    for i in range(total_plateholders) :
        stack_pos = grid.find_object(grid.stack_list[total_plateholders - i - 1])
        grid_pos = plateholder_petri_pos[-1-i][0]
        x_id = grid_pos.x_id
        y_id = grid_pos.y_id
        total_petri = plateholder_petri_pos[-1-i][1]
        for n in range(total_petri) :
            petri_top = grid.object_grid[y_id][x_id][-1]
            petri_bottom = grid.object_grid[y_id][x_id][-2]
            target = [petri_bottom, petri_top]
            await robot.pick_and_place(target, pic_pos)
            # print('pick ', x_id, y_id, target[0]._associated_experiment, target[0].associated_name)
            # grid.remove_object(target)
            await robot.take_picture(obj=target[0], obj_rem=target[1], folder_name=target[0]._associated_experiment,
                                    prefix="marker_" + str(target[0].number) + "_",
                                    suffix="_" + str(target[0].associated_name), to_save = True, pic_pos=pic_pos)
            await robot.pick_and_place(target, stack_pos)
            # print('place ', target[0]._associated_experiment, target[0].associated_name,  'to ', stack_pos.x_id, stack_pos.y_id)





asyncio.run(main())
    
