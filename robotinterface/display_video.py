import os
import sys
import platform
from experiment_helper import *
if platform.system() == 'Windows':
    sys.path.append(os.path.join(sys.path[0], '..'))

import logging
import asyncio
from hardware_control.robot import Robot
from logistics.grid import Grid, GridPosition
from logistics.grid_utils import fill_grid, get_plateholder_petri_pos
from gui.gui import InteractiveWindow
from concurrent.futures import ThreadPoolExecutor
from hardware_control import constants

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

def mouse_callback(event, x, y, flags, param) :
    if event == cv2.EVENT_MOUSEMOVE :
        pixel_value = combined_images[y, x]
        cv2.putText(combined_images, str(pixel_value), (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)



async def main():
    global combined_images
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

    # Go to a position
    await robot.change_tool("camera")
    await robot.gripper.rotate(90)
    x_id = 0 
    y_id = 0
    grid_pos = GridPosition(x_id, y_id)
    x, y = grid.get_coordinates_from_grid(grid_pos)
    await robot.platform.move(x, y, constants.HOVER_CLERANCE, constants.FEEDRATE)

    # Show video
    # await robot.camera.show_video()
    size = (1280, 360)
    while True:
        frame = await robot.camera.camera.capture_frame()

        left_side = 290
        right_side = 780
        upper_side = 420
        bottom_side = 1420

        im_cropped = frame[left_side:right_side, upper_side:bottom_side]

        red_square = frame[25:170, 540:700]
        y_square = 82
        x_square = 68
        hsv_ref = cv2.cvtColor(red_square, cv2.COLOR_BGR2HSV)[y_square, x_square]
        h = hsv_ref[0]
        margin = 3

        # Threshold the HSV image to get only red colors
        if abs(h - 0) < abs(h - 180) :
            lower_h1 = (h-margin)%180
            higher_h1 = 180 if h-margin < 0 else h+margin
            lower_h2 = max(h-margin, 0)
            higher_h2 = h+margin

        else :
            lower_h1 = h-margin
            higher_h1 = min(h+margin, 180)
            lower_h2 = 0 if h+margin > 180 else h-margin
            higher_h2 = (h+margin)%180 if (h+margin)%180 != 0 else 180

        lower_s = 190
        higher_s = 255
        lower_v = 145
        higher_v = 255
        hsv_lower1 = np.array([lower_h1, lower_s, lower_v])
        hsv_higher1 = np.array([higher_h1, higher_s, higher_v])
        hsv_lower2 = np.array([lower_h2, lower_s, lower_v])
        hsv_higher2 = np.array([higher_h2, higher_s, higher_v])

        mask1 = cv2.inRange(cv2.cvtColor(im_cropped, cv2.COLOR_BGR2HSV), hsv_lower1, hsv_higher1)
        mask2 = cv2.inRange(cv2.cvtColor(im_cropped, cv2.COLOR_BGR2HSV), hsv_lower2, hsv_higher2)
        mask = cv2.bitwise_or(mask1, mask2)

        nb_pixel = np.count_nonzero(mask)

        blue_color = (255, 0, 0) # BGR format
        im_cropped[np.where(mask != 0)] = blue_color

        hsv_frame = frame.copy()
        hsv_frame = cv2.cvtColor(hsv_frame, cv2.COLOR_BGR2HSV)

        combined_images = cv2.hconcat([frame, hsv_frame])

        cv2.putText(combined_images, str(nb_pixel) + " red pixels detected", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)    
        cv2.imshow('frame', cv2.resize(combined_images, size))
        # cv2.imshow('detection', cv2.resize(im_cropped, size))
        # Break the loop if 'q' is pressed

        cv2.setMouseCallback('frame', mouse_callback, param=combined_images)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    

    # shutdown the robot
    await robot.shutdown()

asyncio.run(main())