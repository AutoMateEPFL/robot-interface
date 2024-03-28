
import asyncio
from logistics.grid import Grid, GridPosition
from logistics.grid_utils import fill_all
from hardware_control.robot import Robot
import numpy as np
from hardware_control import constants



async def take_picture_of_all_postitions(grid : Grid, robot : Robot, number_plateholder=8, max_plate=12) -> None :
    await robot.change_tool("camera")
    await robot.gripper.rotate(90)
    for i in range(number_plateholder) :
        x_id = 0 if i in [0, 1, 2, 3] else 1
        y_id = i if i in [0, 1, 2, 3] else i - number_plateholder
        print(x_id, y_id)
        grid_pos = GridPosition(x_id, y_id)
        x, y = grid.get_coordinates_from_grid(grid_pos)
        await robot.platform.move(x, y, constants.CLERANCE, constants.FEEDRATE)
        await robot.save_picture(folder_name="CV_take_pic_of_all_pos" ,to_save=True)

    await robot.gripper.rotate(0)
    await robot.change_tool("gripper")

        

