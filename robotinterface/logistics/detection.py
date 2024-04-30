import asyncio
from logistics.grid import Grid, GridPosition
from logistics.grid_utils import fill_all
from hardware_control.robot import Robot
import numpy as np
from hardware_control import constants
from logistics.non_pickable import PlateHolder
from logistics.pickable import *
from logistics.computer_vision_utils import compute_number_plates


async def detect_plates(grid : Grid, robot : Robot, number_plateholder=8) :
    n_plates = np.zeros((2, 4))
    await robot.change_tool("camera")
    await robot.gripper.rotate(90)
    for i in range(number_plateholder) :
        x_id = 0 if i in [0, 1, 2, 3] else 1
        y_id = i if i in [0, 1, 2, 3] else i - 4
        print(x_id, y_id)
        grid_pos = GridPosition(x_id, y_id)
        x, y = grid.get_coordinates_from_grid(grid_pos)
        await robot.platform.move(x, y, constants.HOVER_CLERANCE, constants.FEEDRATE)

        await asyncio.sleep(0.65)
        frame = await robot.camera.camera.capture_frame()

        n_plates[x_id][y_id] = compute_number_plates(frame)

    await robot.gripper.rotate(0)
    await robot.change_tool("gripper")

    return np.int32(n_plates)
