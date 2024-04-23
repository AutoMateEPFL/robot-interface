
import asyncio
from logistics.grid import Grid, GridPosition
from logistics.grid_utils import fill_all
from hardware_control.robot import Robot
import numpy as np
from hardware_control import constants
from logistics.non_pickable import PlateHolder
from logistics.pickable import *



async def take_picture_of_all_postitions(grid : Grid, robot : Robot, number_plateholder=8, max_plate=12) -> None :
    await robot.change_tool("camera")
    await robot.gripper.rotate(90)
    for i in range(number_plateholder) :
        x_id = 0 if i in [0, 1, 2, 3] else 1
        y_id = i if i in [0, 1, 2, 3] else i - number_plateholder
        print(x_id, y_id)
        grid_pos = GridPosition(x_id, y_id)
        x, y = grid.get_coordinates_from_grid(grid_pos)
        await robot.platform.move(x, y, constants.HOVER_CLERANCE, constants.FEEDRATE)
        await robot.save_picture(folder_name="CV_take_pic_of_all_pos" ,to_save=True)

    await robot.gripper.rotate(0)
    await robot.change_tool("gripper")

async def take_n_pictures_of_one_pos(grid : Grid, robot : Robot, number_plates, grid_pos : GridPosition) :
    x_id = grid_pos.x_id
    y_id = grid_pos.y_id
    for _ in range(number_plates) :

        await robot.change_tool("camera")
        petri_top = grid.object_grid[y_id][x_id][-1]
        petri_bottom = grid.object_grid[y_id][x_id][-2]
        target = [petri_bottom, petri_top]
        await robot.gripper.rotate(90)
        await robot.platform.move(x_id, y_id, constants.HOVER_CLERANCE, constants.FEEDRATE)
        await robot.save_picture(folder_name="CV_take_n_pic_of_one_pos" ,to_save=True)
        await robot.gripper.rotate(0)
        await robot.change_tool("gripper")
        await robot.pick_and_place(target, GridPosition(2, 0))

    #pic of empty plateholder
    await robot.change_tool("camera")
    await robot.gripper.rotate(90)
    await robot.platform.move(x_id, y_id, constants.HOVER_CLERANCE, constants.FEEDRATE)
    await robot.save_picture(folder_name="CV_take_n_pic_of_one_pos" ,to_save=True)
    await robot.gripper.rotate(0)
    await robot.change_tool("gripper")
