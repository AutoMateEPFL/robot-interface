# poetry run python robotinterface\protocol.py
# Interpreter path
# C:\Users\APrap\AppData\Local\pypoetry\Cache\virtualenvs\robotinterface-u1VIN2jz-py3.10

import logging
import asyncio

from robotinterface.hardware_control.robot import Robot

from robotinterface.logistics.grid import Grid, GridPosition
from robotinterface.logistics.pickable import *

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')


async def main():
    grid = Grid(x_max=-820, x_dist=-200, y_max=-610, y_dist=-120)

    end_pos = GridPosition(0, grid.y_num_interval-1)
    zero_pos = GridPosition(1, grid.y_num_interval-1)
    cover_pos = GridPosition(0, grid.y_num_interval-2)
    
    petri_bottom = SmallPetriBottom()
    petri_top = SmallPetriTop()
    petri_bottom1 = SmallPetriBottom()
    petri_top1 = SmallPetriTop()

    grid.add_object([petri_bottom, petri_top], zero_pos)
    grid.add_object([petri_bottom1, petri_top1], end_pos)
    grid.add_object([PlateHolder()], end_pos)
    grid.add_object([PlateHolder()], zero_pos)

    # grid.add_object([plateHolders[1]], end_pos)
    
    robot = await Robot.build(grid)
    next_pos = end_pos
    while True:
        input("Press Enter to continue...")
        await robot.pick_and_place([petri_bottom, petri_top], next_pos)
        await robot.pick_and_place([petri_top], cover_pos)
        await robot.pick_and_place([petri_top], next_pos)
        if next_pos == end_pos:
            next_pos = zero_pos
        else:
            next_pos = end_pos
        
    await robot.shutdown()
        
    # await  robot.pick_and_place([petri_bottom, petri_top], end_pos)
    # input("Press Enter to continue...")
    
    
    
    
    
    # print(list_of_of_objects[1].id)
    # robot = await Robot.build(grid)
    # input("Press Enter to continue...")
    # await  robot.pick_and_place([petri_bottom, petri_top], end_pos)
    # input("Press Enter to continue...")
    
    # await robot.move(GridPosition(0, 0), 200)
    # input("Press Enter to move to position ...")
    # await robot.move(GridPosition(1, grid.y_num_interval-1), 200)
    # input("Press Enter to move to position ...")
    # await robot.change_tool("Camera")
    # await robot.move(GridPosition(1, grid.y_num_interval-1), 200)
    # input ("Press Enter to continue...")
    # await robot.change_tool("error test")
    # await robot.move(GridPosition(2, 0), 200)
    # input("Press Enter to move to position 0,1 ...")
    # await robot.move(GridPosition(0, 2), 200)
    # input("Press Enter to move to position...")
    # print("Moving to position ", grid.x_num_interval -1, grid.y_num_interval-1, "...")
    # await robot.move(GridPosition(grid.x_num_interval-1, grid.y_num_interval-1), 200)
    # input("Press Enter to continue...")

    # await robot.pick_and_place([bottom4, top4],
    #                            GridPosition(1, 3))
    # await robot.pick_and_place([top4], GridPosition(1, 4))

    # await robot.pick_and_place([top4], GridPosition(1, 3))
    # await robot.pick_and_place([bottom4, top4],
    #                            end_pos)

    # await robot.shutdown()


asyncio.run(main())
