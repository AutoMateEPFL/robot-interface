import sys
import logging
import asyncio
import glob
import os
import platform
import cv2
import numpy as np
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

def analyse_each_image_separately(folder_name, auto_offset=False, auto_rotate=False,num_cols=10):
    images = glob.glob(folder_name+'/*.jpg')
    num_cols = num_cols
    #auto_rotate = False
    if num_cols == 10:
        positions = [(240, 240), (880, 810)]
    elif num_cols == 9:
        positions = [(200, 250), (780, 830)]
    for image in images :
        print(image)
        input_image = cv2.imread(image)
        tall = input_image.shape[0]
        width =  input_image.shape[1]

        #cropped_input = input_image[:,(width-tall)//2:width-(width-tall)//2][:]

        cropped_input = input_image[:, 430:1560][:]

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
        matrix, matrix_of_keypoints, new_offset = analyse_matrix(rotated_image, positions, draw_blob=True, auto_offset=auto_offset,num_cols=num_cols)

        if auto_rotate:
            #print(matrix)
            #print(matrix[0,:])
            max_dist = 0
            for i in range(0,len(matrix[:,0])):
                line = matrix[i,:]
                #print(line)
                line_index = 0
                #print(np.where(line == 1)[0])
                if np.linalg.norm(line) > 0:
                    first_index = np.where(line == 1)[0][0]
                    last_index = np.where(line == 1)[0][-1]
                    if abs( last_index-first_index)>max_dist:
                        max_dist = abs( last_index-first_index)
                        my_first_index = first_index
                        my_last_index = last_index
                        line_index = i
            #print('where first',np.where(line == 1)[0][0])
            #print('where last', np.where(line == 1)[0][-1])
            #print('I',line_index)
            first_point = matrix_of_keypoints[line_index][my_first_index]
            last_point = matrix_of_keypoints[line_index][my_last_index]
            theta= np.arctan((first_point.pt[1]-last_point.pt[1])/(first_point.pt[0]-last_point.pt[0]))
            print('THETA',theta)
            rotated_image = rotateImage(cropped_input, -angle+theta)
            cv2.putText(rotated_image, str(round(angle-theta, 2)), (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2,
                        cv2.LINE_AA)

            matrix, matrix_of_keypoints, new_offset = analyse_matrix(rotated_image, positions, draw_blob=True,
                                                                     auto_offset=auto_offset,num_cols=num_cols)

        #new_offset = [0,0]
        new_positions = [(positions[0][0]+new_offset[0],positions[0][1]+new_offset[1]),
                         (positions[1][0]+new_offset[0],positions[1][1]+new_offset[1])]

        output = draw_resutls(rotated_image, new_positions, matrix,num_cols=num_cols)

        cv2.imshow('Input', cropped_input)
        cv2.imshow('Output', output)
        cv2.imwrite(image.replace('.jpg','')+"_out.jpeg",output)

def summary_of_all_images(folder_name):
    input_images = glob.glob(folder_name + '/*.jpg')
    output_images = glob.glob(folder_name+'/*'+'_out.jpeg')
    print(input_images)
    print(output_images)
    tall = cv2.imread(input_images[0]).shape[0]
    width = cv2.imread(input_images[0]).shape[1]

    #input_summary = cv2.imread(input_images[0])[:, (width - tall) // 2:width - (width - tall) // 2][:]
    input_summary = cv2.imread(input_images[0])[:, 430:1560][:]
    output_summary = cv2.imread(output_images[0])

    for i in range(1,len(input_images)) :
        #input_summary= np.concatenate((input_summary, cv2.imread(input_images[i])[:, (width - tall) // 2:width - (width - tall) // 2][:]), axis=0)
        input_summary= np.concatenate((input_summary, cv2.imread(input_images[i])[:, 430:1560][:]), axis=1)
        output_summary = np.concatenate((output_summary, cv2.imread(output_images[i])), axis=1)

    image_summary = np.concatenate((input_summary, output_summary), axis=0)

    cv2.imwrite( folder_name+"/image_summary.jpeg", image_summary)



if __name__ == "__main__":
    #/Users/Etienne/Documents/GitHub/robot-interface/images/test
    #/Users/Etienne/Documents/GitHub/robot-interface/images/1_trait
    analyse_each_image_separately("/Users/Etienne/Documents/GitHub/robot-interface/images/demo", auto_offset=True, auto_rotate=False,num_cols=9)
    summary_of_all_images("/Users/Etienne/Documents/GitHub/robot-interface/images/demo")
