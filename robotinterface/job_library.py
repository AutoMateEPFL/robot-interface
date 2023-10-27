import sys
import logging
import asyncio
import glob
import os
import platform
import cv2
if platform.system() == 'Windows':
    sys.path.append(os.path.join(sys.path[0],'..'))
else:
    sys.path.append(r"/Users/Etienne/Documents/GitHub/robot-interface")

from Computer_vision.Image_processing.cv_matrix import analyse_matrix, draw_resutls
from Computer_vision.Image_processing.cv_orientation import rotateImage, fing_perti_angle



def find_all_experiments(grid):
    list_of_experiments = []
    for x in range(grid.x_num_interval):
        for y in range(grid.y_num_interval):
            if grid.object_grid[y][x] != []:
                print('grid', grid.object_grid[y][x][0])
                print(str(type(grid.object_grid[y][x][0])) == "<class 'logistics.pickable.PlateHolder'>")
                if str(type(grid.object_grid[y][x][0])) == "<class 'logistics.pickable.PlateHolder'>":
                    print('EXPERIMENT FOUND', x, y)
                    list_of_experiments.append(grid.object_grid[y][x][0])
    return list_of_experiments

async def take_photo_of_all_experiments_and_reconstruct_piles(robot, grid, pic_pos, stack_pos):

    # FIND ALL EXPERIMENTS IN THE GRID, FOR NOW ONE EXPERIMENT = ONE PLATEHOLDER

    list_of_experiments = find_all_experiments(grid)

    # FOR EACH EXPERIMENT TAKE PICTURES AND DECONSTRUCT THE PILE

    for experiment in list_of_experiments:
        pos_experiment = grid.find_object(experiment)
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

            await robot.take_picture(target[0], obj_rem=target[1], folder_name="", suffix="_"+str(target[0].name))
            await robot.pick_and_place(target, stack_pos)

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

def analyse_each_image_separately(folder_name):
    images = glob.glob(folder_name+'/*.jpg')
    auto_rotate = False
    positions = [(280, 280), (850, 850)]
    for image in images :
        print(image)
        input_image = cv2.imread(image)
        tall = input_image.shape[0]
        width =  input_image.shape[1]

        cropped_input = input_image[:,(width-tall)//2:width-(width-tall)//2][:]

        print(cropped_input.shape)

        # Correction for the rotation of the image
        angle = fing_perti_angle(cropped_input)
        if angle is not None:
            rotated_image = rotateImage(cropped_input, -angle)
            #output = cropped_input
        else:
            rotated_image = cropped_input.copy()
            angle = 0

        cv2.putText(rotated_image, str(round(angle, 2)), (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

        # Analyse the results
        matrix, new_offset = analyse_matrix(rotated_image, positions, draw_blob=True)
        #new_offset = [0,0]
        new_positions = [(positions[0][0]+new_offset[0],positions[0][1]+new_offset[1]),
                         (positions[1][0]+new_offset[0],positions[1][1]+new_offset[1])]

        output = draw_resutls(rotated_image, new_positions, matrix)

        cv2.imshow('Input', cropped_input)
        cv2.imshow('Output', output)
        cv2.imwrite(image.replace('.jpg','')+"_out.jpeg",output)

if __name__ == "__main__":
    analyse_each_image_separately("/Users/Etienne/Documents/GitHub/robot-interface/images/2")
