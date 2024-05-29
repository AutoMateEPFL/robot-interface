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
from logistics.computer_vision_utils import *

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')


def mouse_callback(event, x, y, flags, param) :
    if event == cv2.EVENT_LBUTTONDBLCLK :
        image = param
        pixel_value = image[y, x]
        pixel_value_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)[y, x]
        pixel_value_lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)[y, x]
        print(x, y)
        print('bgr : ', pixel_value)
        print('hsv : ', pixel_value_hsv)
        print('lab : ', pixel_value_lab)
        
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

    # Go to a position
    await robot.change_tool("camera")
    await robot.gripper.rotate(90)
    x_id = 0
    y_id = 1
    grid_pos = GridPosition(x_id, y_id)
    x, y = grid.get_coordinates_from_grid(grid_pos)
    await robot.platform.move(x, y, constants.HOVER_CLERANCE, constants.FEEDRATE)

    # Show video
    # await robot.camera.show_video()
    size = (1280, 360)
    middle_values = [78946, 65497, 59481, 54604, 48136, 40231, 32417, 21347, 10108]
    number_plates = 0
    MODE = 1
    robot.camera.camera.cap.set(cv2.CAP_PROP_AUTO_WB, 1)
    robot.camera.camera.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
    while True:
        if MODE == 0 :
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
            lower_v = 50
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

            # draw detection zone of the red square 
            cv2.rectangle(hsv_frame, (540,25), (700,170), color=(0,0,0), thickness=3)

            combined_images = cv2.hconcat([frame, hsv_frame])

            if nb_pixel > np.max(middle_values) :
                number_plates = 0
            elif nb_pixel < np.min(middle_values) :
                number_plates = 9
            else :
                positions = [i for i in range(len(middle_values)-1) if middle_values[i] >= nb_pixel >= middle_values[i+1]]
                if len(positions) > 1 :
                    number_plates = -1
                    cv2.putText(combined_images, "multiple number of plates possible", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 4)
                else :
                    number_plates = positions[0] + 1
            
            cv2.putText(combined_images, str(number_plates) + " plates detected", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 4)

            cv2.putText(combined_images, str(nb_pixel) + " red pixels detected", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 4) 
            cv2.imshow('frame', cv2.resize(combined_images, size))

            cv2.setMouseCallback('frame', mouse_callback, param=cv2.resize(combined_images, size))
            # cv2.imshow('detection', cv2.resize(im_cropped, size))
            # Break the loop if 'q' is pressed

            if cv2.waitKey(1) & 0xFF == ord('q'):
             break

        elif MODE == 1 :
            size = (1280, 720)
            holder_ul = (390,290)
            holder_br = (1380,780)
            reference_ul = (540,50) # x y format
            reference_br = (640,140)

            frame = await robot.camera.camera.capture_frame(focus=constants.FOCUS)

            number_plates, mask, reference = compute_number_plates_lab(frame, reference_ul, reference_br, holder_ul, holder_br)

            im_displayed = frame.copy()
            im_cropped = frame[holder_ul[1]:holder_br[1], holder_ul[0]:holder_br[0]]
            # add blue color
            im_cropped[np.where(mask != 0)] = (255, 0, 0)
            im_displayed[holder_ul[1]:holder_br[1], holder_ul[0]:holder_br[0]] = im_cropped
            cv2.rectangle(im_displayed, reference_ul, reference_br, (0,0,0), 4)
            cv2.rectangle(im_displayed, holder_ul, holder_br, (0,0,0), 4)

            im_displayed = cv2.resize(im_displayed, size)
            
            cv2.putText(im_displayed, str(number_plates) + " plates detected", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 3)
            number_pixels = np.count_nonzero(mask)
            cv2.putText(im_displayed, str(number_pixels) + " pixels detected", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 3)

            cv2.imshow('image_displayed', im_displayed)

            cv2.setMouseCallback('image_displayed', mouse_callback, param=im_displayed)
            # cv2.imshow('detection', cv2.resize(im_cropped, size))
            # Break the loop if 'q' is pressed

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        


        
    await robot.gripper.rotate(0)
    await robot.change_tool("gripper")
    await robot.gripper.rotate(0)
    # shutdown the robot
    await robot.shutdown()

asyncio.run(main())