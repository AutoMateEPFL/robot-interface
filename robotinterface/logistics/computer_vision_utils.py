
import asyncio
from logistics.grid import Grid, GridPosition
from logistics.grid_utils import fill_all
from hardware_control.robot import Robot
import numpy as np
from hardware_control import constants
from logistics.non_pickable import PlateHolder
from logistics.pickable import *
import cv2



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
        grid_pos = GridPosition(x_id, y_id)
        x, y = grid.get_coordinates_from_grid(grid_pos)
        await robot.platform.move(x, y, constants.HOVER_CLERANCE, constants.FEEDRATE)
        await robot.save_picture(folder_name="CV_take_n_pic_of_one_pos" ,to_save=True)
        await robot.gripper.rotate(0)
        await robot.change_tool("gripper")
        await robot.pick_and_place(target, GridPosition(2, 0))

    #pic of empty plateholder
    await robot.change_tool("camera")
    await robot.gripper.rotate(90)
    grid_pos = GridPosition(x_id, y_id)
    x, y = grid.get_coordinates_from_grid(grid_pos)
    await robot.platform.move(x, y, constants.HOVER_CLERANCE, constants.FEEDRATE)
    await robot.save_picture(folder_name="CV_take_n_pic_of_one_pos" ,to_save=True)
    await robot.gripper.rotate(0)
    await robot.change_tool("gripper")

def compute_number_plates(frame) :
    middle_values = [80718, 66168, 59409, 53988, 48250, 41469, 34268, 24209, 9716]

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

    if nb_pixel > np.max(middle_values) :
        number_plates = 0
    elif nb_pixel < np.min(middle_values) :
        number_plates = 9
    else :
        positions = [i for i in range(len(middle_values)-1) if middle_values[i] >= nb_pixel >= middle_values[i+1]]
        if len(positions) > 1 :
            number_plates = -1
        else :
            number_plates = positions[0] + 1

    # number plates = -1 if nb_pixels falls exactly in a middle value
    return number_plates

def get_lab_reference(im_lab, ref_ul, ref_br) :
    reference = im_lab[ref_ul[1]:ref_br[1], ref_ul[0]:ref_br[0], :]
    ref_l, ref_a, ref_b = cv2.split(reference)
    a = np.mean(ref_a)
    b = np.mean(ref_b)
    lab_reference = [0, a, b]
    return lab_reference

def create_lab_mask(im_lab, lab_value, a_margin, b_margin) :
    a = lab_value[1]
    b = lab_value[2]
    lower_bound = np.array([0, a-a_margin, b-b_margin])
    upper_bound = np.array([255, a+a_margin, b+b_margin])
    mask = cv2.inRange(im_lab, lower_bound, upper_bound)
    return mask

def compute_number_plates_lab(im, ref_ul, ref_br, region_ul, region_br, reference=None) :
    im_lab = cv2.cvtColor(im, cv2.COLOR_BGR2LAB)
    # Thresholds computed for the (0,0) position specifically
    middle_values = [78946, 65497, 59481, 54604, 48136, 40231, 32417, 21347, 10108]
    # Thresholds computed based on all positions, less precise depending on position
    # middle_values = [75080, 60451, 55730, 50327, 45612, 37902, 29470, 17665, 6011]
    if reference == None :
        lab_reference = get_lab_reference(im_lab, ref_ul, ref_br)
    else :
        lab_reference = reference
    im_cropped = im_lab[region_ul[1]:region_br[1], region_ul[0]:region_br[0]]
    a_margin = 17
    b_margin = 17
    mask = create_lab_mask(im_cropped, lab_reference, a_margin, b_margin)

    nb_pixel = np.count_nonzero(mask)

    if nb_pixel > np.max(middle_values) :
        number_plates = 0
    elif nb_pixel < np.min(middle_values) :
        number_plates = 9
    else :
        positions = [i for i in range(len(middle_values)-1) if middle_values[i] >= nb_pixel >= middle_values[i+1]]
        if len(positions) > 1 :
            number_plates = -1
        else :
            number_plates = positions[0] + 1

    # number plates = -1 if nb_pixels falls exactly in a middle value
    return number_plates, mask, lab_reference