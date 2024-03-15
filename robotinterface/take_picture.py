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
from logistics.pickable import *
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
    if platform.system() == 'Windows':
        robot = await Robot.build(grid)

    grid.add_object([SmallPetriBottom(),
                     SmallPetriTop()],
                     GridPosition(2,1))

    await robot.take_picture(obj=grid.object_grid[1][2][-1],  folder_name='take_picture', to_save = True)
    # print('place ', target[0]._associated_experiment, target[0].associated_name,  'to ', stack_pos.x_id, stack_pos.y_id)
    
    # shutdown the robot
    await robot.shutdown()





asyncio.run(main())
    
