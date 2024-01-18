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
    sys.path.append(os.path.join(sys.path[0], '..'))
    splitter = "\\"
else:
    # sys.path.append(r"/Users/Etienne/Documents/GitHub/robot-interface")
    sys.path.append(os.path.join(sys.path[0], '..'))
    splitter = "/"

def find_all_PlateHolder(grid):
    "Return all plate holders on the grid, plate holder are used to define a pile"
    list_of_experiments = []
    for x in range(grid.x_num_interval):
        for y in range(grid.y_num_interval):
            if grid.object_grid[y][x] != []:
                print('grid', grid.object_grid[y][x][0])
                print(str(type(grid.object_grid[y][x][0])) == "<class 'logistics.non_pickable.PlateHolder'>")
                if str(type(grid.object_grid[y][x][0])) == "<class 'logistics.non_pickable.PlateHolder'>":
                    print('EXPERIMENT FOUND', x, y)
                    list_of_experiments.append(grid.object_grid[y][x][0])
    return list_of_experiments

def save_datalog_of_a_plateholder(plateholder):
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
    # for names i

    text = "EXPERIMENT LOG, date : " + timestamp + " , name : " + plateholder.associated_name + '\n'
    text += ("LIST OF MARKER NAMES FROM GROUND TO TOP :")
    if platform.system() == 'Windows':
        path = os.path.join('images', plateholder.associated_name)
    else:
        path = os.path.join('..', 'images', plateholder.associated_name)
    # path = "../images/"+experiment.associated_name
    equivalent_names = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'k']

    for eq, marker in zip(equivalent_names, plateholder.experiment.marker_list):
        text += ('\n')
        text += ("Marker " + str(eq) + " : " + str(marker))

    # Ensure the images directory exists
    os.makedirs(path, exist_ok=True)

    # with open(path+"/"+experiment.associated_name+'_info.txt', 'w') as f:
    with open(os.path.join(path, experiment.associated_name + '_info.txt'), 'w') as f:
        f.write(text)
