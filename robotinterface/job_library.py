import sys
import logging
import asyncio
import glob
import os
import platform
import cv2
import numpy as np
import datetime

if platform.system() == 'Windows':
    sys.path.append(os.path.join(sys.path[0],'..'))
    splitter = "\\"
else:
    sys.path.append(r"/Users/Etienne/Documents/GitHub/robot-interface")
    splitter = "/"

from Computer_vision.Image_processing.cv_matrix import analyse_matrix, draw_resutls
from Computer_vision.Image_processing.cv_orientation import rotateImage, fing_petri_angle, detect_sticker

def find_all_PlateHolder(grid):
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


def rotation_correction(matrix,matrix_of_keypoints,positions, cropped_input, angle, auto_offset, num_cols):

    max_dist = 0
    for i in range(0, len(matrix[:, 0])):
        line = matrix[i, :]
        # print(line)
        line_index = 0
        # print(np.where(line == 1)[0])
        if np.linalg.norm(line) > 0:
            first_index = np.where(line == 1)[0][0]
            last_index = np.where(line == 1)[0][-1]
            if abs(last_index - first_index) > max_dist:
                max_dist = abs(last_index - first_index)
                my_first_index = first_index
                my_last_index = last_index
                line_index = i

    first_point = matrix_of_keypoints[line_index][my_first_index]
    last_point = matrix_of_keypoints[line_index][my_last_index]
    theta = np.arctan((first_point.pt[1] - last_point.pt[1]) / (first_point.pt[0] - last_point.pt[0]))
    print('THETA', theta)
    rotated_image = rotateImage(cropped_input, -angle + theta)
    cv2.putText(rotated_image, str(round(angle - theta, 2)), (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2,
                cv2.LINE_AA)

    matrix, matrix_of_keypoints, new_offset = analyse_matrix(rotated_image, positions, draw_blob=False,
                                                             auto_offset=auto_offset, num_cols=num_cols)

def analyse_each_image_separately(folder_name, method='sticker', auto_offset=False, auto_rotate=False,num_cols=10,aggregation = False):
    experiment_name = folder_name.split("/")[-1]
    path = os.path.join(folder_name,'*.jpg')
    #images = sorted(glob.glob(folder_name+'/*.jpg'))
    images = sorted(glob.glob(path))
    num_cols = num_cols
    #auto_rotate = False
    if num_cols == 10:
        positions = [(240, 240), (880, 810)]
    elif num_cols == 9:
        positions_saarstedt = [(240, 245), (800, 830)]
        positions_corning = [(300, 250), (820, 830)]
        #positions_corning = [(230, 250), (880, 810)]
        positions = positions_corning

    matrix_list = []
    marker_names_list = []
    print(images)

    for image in images :
        marker_names_list.append(image.split("_")[-1][:-4])
        print('marker_names_list',marker_names_list)

        input_image = cv2.imread(image)
        #tall = input_image.shape[0]
        #width =  input_image.shape[1]
        #cropped_input = input_image[:,(width-tall)//2:width-(width-tall)//2][:]

        cropped_input = input_image[:1050, 430:1490][:]

        # Correction for the rotation of the image
        if method=='sticker':
            angle = detect_sticker(cropped_input)
        elif method=='line':
            angle = fing_petri_angle(cropped_input)
        else :
            angle = fing_petri_angle(cropped_input)
        if angle is not None:
            rotated_image = rotateImage(cropped_input, -angle)
        else:
            rotated_image = cropped_input.copy()
            angle = 0

        cv2.putText(rotated_image, str(round(angle, 2)), (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
        if image == images[0]:
            background = rotated_image.copy()

        # Analyse the results
        matrix, matrix_of_keypoints, new_offset = analyse_matrix(rotated_image, positions, draw_blob=False, auto_offset=auto_offset,num_cols=num_cols)[0:3]

        if auto_rotate:
            rotation_correction(matrix=matrix, matrix_of_keypoints=matrix_of_keypoints, positions=positions,
                                cropped_input=cropped_input, angle=angle, auto_offset=auto_offset, num_cols=num_cols)
        matrix_list.append(matrix)

        new_positions = [(positions[0][0]+new_offset[0],positions[0][1]+new_offset[1]),
                         (positions[1][0]+new_offset[0],positions[1][1]+new_offset[1])]
        if image == images[0]:
            new_positions_0 = new_positions
        output = draw_resutls(rotated_image, new_positions, matrix,num_cols=num_cols)

        cv2.imwrite(image.replace('.jpg','')+"_out.jpeg",output)

    if aggregation:
        aggregated_image = create_aggregated_matrix(matrix_list=matrix_list, marker_names_list=marker_names_list,
                                                    positions=new_positions_0, num_cols=num_cols,background=background,
                                                    experiment_name=folder_name.split(splitter)[-1])
        path = os.path.join(folder_name, "aggregated_matrix_"+experiment_name+".jpeg")
        #cv2.imwrite(folder_name + "/aggregated_matrix.jpeg", aggregated_image)
        cv2.imwrite(path, aggregated_image)

def summary_of_all_images(folder_name):
    experiment_name = folder_name.split("/")[-1]
    path_input = os.path.join(folder_name, '*.jpg')
    #input_images = sorted(glob.glob(folder_name + '/*.jpg'))
    input_images = sorted(glob.glob(path_input))

    path_output = os.path.join(folder_name, '*_out.jpeg')
    #output_images = sorted(glob.glob(folder_name+'/*'+'_out.jpeg'))
    output_images = sorted(glob.glob(path_output))

    print(input_images)
    print(output_images)
    tall = cv2.imread(input_images[0]).shape[0]
    width = cv2.imread(input_images[0]).shape[1]

    #input_summary = cv2.imread(input_images[0])[:, (width - tall) // 2:width - (width - tall) // 2][:]
    input_summary = cv2.imread(input_images[0])[:1050, 430:1490][:]
    output_summary = cv2.imread(output_images[0])
    cv2.putText(output_summary, "Marker: " + str(input_images[0].split("_")[-1][:-4]), (320, 220),
                cv2.FONT_HERSHEY_SIMPLEX, 1.7, (255, 0, 0), 2, cv2.LINE_AA)

    for i in range(1,len(input_images)) :

        #input_summary= np.concatenate((input_summary, cv2.imread(input_images[i])[:, (width - tall) // 2:width - (width - tall) // 2][:]), axis=0)
        input_summary= np.concatenate((input_summary, cv2.imread(input_images[i])[:1050, 430:1490][:]), axis=1)
        output_to_aggregate = cv2.imread(output_images[i])
        cv2.putText(output_to_aggregate, "Marker: " + str(input_images[i].split("_")[-1][:-4]), (320, 220),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.7, (255, 0, 0), 2, cv2.LINE_AA)
        output_summary = np.concatenate((output_summary, output_to_aggregate), axis=1)

    image_summary = np.concatenate((input_summary, output_summary), axis=0)

    path = os.path.join(folder_name, "image_summary_"+experiment_name+".jpeg")
    #cv2.imwrite( folder_name+"/image_summary.jpeg", image_summary)
    cv2.imwrite(path, image_summary)


def create_aggregated_matrix(matrix_list,marker_names_list,positions,num_cols,background=0,experiment_name=""):
    N = len(matrix_list)
    equivalent_names = ['a','b','c','d','e','f','g','h','k']
    if background.all == 0 :
        image = np.zeros((1000,1000,3))
        image = cv2.imread("/Users/Etienne/Documents/GitHub/robot-interface/images/20230817153856.jpg")[:,430:1430]
    else:
        #image = cv2.imread(background)[:,430:1430]
        image = background
    print('marker_names_list',marker_names_list)

    if experiment_name != "":
        cv2.putText(image, "Experiment: "+str(experiment_name), (320,220),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.7, (255, 255, 255), 2, cv2.LINE_AA)

    if len(positions) >= 2:
        num_cols: int = num_cols
        num_rows: int = 9

        pos0: tuple = positions[0]
        pos1: tuple = positions[1]
        offset: tuple = ((pos1[0] - pos0[0]) / num_cols, (pos1[1] - pos0[1]) / num_rows)

        for i in range(num_cols):
            for j in range(num_rows):
                if j == 4:
                    continue

                pt1: tuple = int(pos0[0] + i * offset[0]), int(pos0[1] + j * offset[1])
                pt2: tuple = int(pos0[0] + (i + 1) * offset[0]) - 1, int(pos0[1] + (j + 1) * offset[1]) - 1
                #BGR

                if j <= 4:
                    if matrix_list[0][i, :4].all() == 1:
                        draw = True
                    else :
                        draw =False
                elif j >=5 :
                    if matrix_list[0][i, 5:].all() == 1:
                        draw = True
                    else :
                        draw =False
                else:
                    draw = False

                if matrix_list[0][i, j] == 1 and draw:
                    cv2.rectangle(image, pt1, pt2, (0, 255, 0), 2)
                else :
                    cv2.rectangle(image, pt1, pt2, (0, 0, 255), 2)

                for k in range(1,N):
                    if matrix_list[k][i,j] and draw:
                        cv2.putText(image, str(equivalent_names[k]), (5+pt1[0]+30*((k-1)%2),-40+pt2[1]+30*(k-1)//2 ),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2, cv2.LINE_AA)
                    cv2.putText(image, str(equivalent_names[k])+" : "+str(marker_names_list[k]),(100, 870+30*k),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
        return image

def save_datalog_of_a_plateholder(plateholder):
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
    #for names i

    text = "EXPERIMENT LOG, date : "+timestamp+ " , name : "+plateholder.associated_name + '\n'
    text+=("LIST OF MARKER NAMES FROM GROUND TO TOP :")
    if platform.system() == 'Windows':
        path = os.path.join( 'images',plateholder.associated_name)
    else:
        path = os.path.join('..', 'images',plateholder.associated_name)
    #path = "../images/"+experiment.associated_name
    equivalent_names = ['a', 'b', 'c', 'd', 'e', 'f']

    for eq, marker in zip(equivalent_names,plateholder.experiment.marker_list):
        text+=('\n')
        text+=("Marker "+str(eq)+" : "+str(marker))

    # Ensure the images directory exists
    os.makedirs(path, exist_ok=True)

    #with open(path+"/"+experiment.associated_name+'_info.txt', 'w') as f:
    with open(os.path.join(path, experiment.associated_name+ '_info.txt'), 'w') as f:
        f.write(text)

if __name__ == "__main__":
    for name in ['a','b','c','d','e','f']:
        analyse_each_image_separately("../images/"+name, auto_offset=True, auto_rotate=True,
                                       num_cols=9,aggregation = True)
        summary_of_all_images("../images/"+name)
