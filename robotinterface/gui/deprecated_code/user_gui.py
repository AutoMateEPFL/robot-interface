import cv2
import numpy as np
from logistics.grid import Grid, GridPosition
from logistics.pickable import *
from logistics.non_pickable import *
from robotinterface.gui.tkinter_pile_object import *
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import platform
import csv
import os

mouseX, mouseY, left_click, right_click, middle_click = 0, 0, False, False, False

if platform.system() == 'Windows':
    prefix = ""
else:
    prefix = ".."


def generate_grid_image(grid: Grid, grid_resolution: int, line_thickness: int):
    """Generates a grid image with the given resolution and line thickness."""

    dark_case = np.ones((grid_resolution, grid_resolution, 3)) * np.array([231 / 255, 212 / 255, 208 / 255])
    light_case = np.ones((grid_resolution, grid_resolution, 3)) * np.array([244 / 255, 234 / 255, 233 / 255])

    print("size of the grid♟️ : ", grid.x_num_interval, "x", grid.y_num_interval)

    line = dark_case
    for i in range(grid.y_num_interval - 1):
        if i % 2 == 0:
            line = np.concatenate((line, np.ones((grid_resolution, line_thickness, 3))), axis=1)
            line = np.concatenate((line, light_case), axis=1)
        else:
            line = np.concatenate((line, np.ones((grid_resolution, line_thickness, 3))), axis=1)
            line = np.concatenate((line, dark_case), axis=1)

    Imshow = line
    for i in range(grid.x_num_interval - 1):
        Imshow = np.concatenate((Imshow, np.ones((line_thickness, Imshow.shape[1], 3))), axis=0)
        Imshow = np.concatenate((Imshow, line), axis=0)

    return np.transpose(Imshow, (1, 0, 2))


def load_light_or_dark(grid_pos, name):
    " Choose between dark and light version of an image for a given grid pos"
    if grid_pos.y_id % 2 == 0:
        model = cv2.imread(os.path.join(prefix, 'robotinterface', 'gui', name + '_dark.png'))
    else:
        model = cv2.imread(os.path.join(prefix, 'robotinterface', 'gui', name + '_light.png'))
    return model


def draw_object(grid_pos: GridPosition, imshow, grid_resolution, line_thickness, name):
    "Draw object using the name, with no condition on displaying"
    model = load_light_or_dark(grid_pos, name)

    width, height = 70, 70
    model = cv2.resize(model, (width, height)) / 255

    x = grid_pos.x_id * (grid_resolution + line_thickness) + grid_resolution // 2 - width // 2
    y = grid_pos.y_id * (grid_resolution + line_thickness) + grid_resolution // 2 - height // 2

    x_end = x + width
    y_end = y + height

    imshow[y:y_end, x:x_end] = model


def mark_H(grid_pos: GridPosition, imshow, grid_resolution, line_thickness):
    """Draws H for holder on the given grid position."""
    cv2.putText(imshow, "H", (
    grid_pos.x_id * (grid_resolution + line_thickness) + 5, grid_pos.y_id * (grid_resolution + line_thickness) + 17),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 2)


def mark_E(grid_pos: GridPosition, imshow, grid_resolution, line_thickness, number):
    """Draws E for experiment on the given grid position, and the number of experiment on the pile."""
    cv2.putText(imshow, "E " + str(number), (
        grid_pos.x_id * (grid_resolution + line_thickness) + 5,
        grid_pos.y_id * (grid_resolution + line_thickness) + 95),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

def mark_P(grid_pos: GridPosition, num, imshow, grid_resolution, line_thickness):
    """Draws P for petridish on the given grid position, and the number of petri dishes on the position."""
    cv2.putText(imshow, str(num), ((grid_pos.x_id + 1) * (grid_resolution + line_thickness) - 20,
                                   grid_pos.y_id * (grid_resolution + line_thickness) + 17),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 2)


def draw_grid(grid: Grid, imshow, grid_resolution, line_thickness):
    """Draw the grid on the imshow"""
    # draw fixed objects
    draw_object(grid.find_object(grid.cam), imshow, grid_resolution, line_thickness, 'camera')

    for stack in grid.stack_list:
        draw_object(stack._grid_position, imshow, grid_resolution, line_thickness, 'stack')
    # draw pickables:
    for x in range(grid.x_num_interval):
        for y in range(grid.y_num_interval):
            num_petri = 0
            holder = False
            for object in grid.object_grid[y][x]:
                if object.name == "Plate Holder":
                    holder = True
                    draw_object(GridPosition(x, y), imshow, grid_resolution, line_thickness, 'holder')
                    mark_E(GridPosition(x, y), imshow, grid_resolution, line_thickness, number=object.num_experiments)
                elif object.name == "Small Petri Top":
                    num_petri += 1
            if num_petri > 0:
                draw_object(GridPosition(x, y), imshow, grid_resolution, line_thickness, 'petri')
                mark_P(GridPosition(x, y), num_petri, imshow, grid_resolution, line_thickness)
            if holder:
                mark_H(GridPosition(x, y), imshow, grid_resolution, line_thickness)


def is_not_stack_or_camera(grid: Grid, grid_pos: GridPosition):
    if len(grid.object_grid[grid_pos.y_id][grid_pos.x_id]) > 0 and grid.object_grid[grid_pos.y_id][grid_pos.x_id][
        0] == grid.cam:
        logging.info("Cannot use Photo spot")
        return False
    elif len(grid.object_grid[grid_pos.y_id][grid_pos.x_id]) > 0 and grid.object_grid[grid_pos.y_id][grid_pos.x_id][
        0] in grid.stack_list:
        logging.info("Cannot use Stack spot")
        return False
    return True


def add_petridish(grid: Grid, grid_pos: GridPosition, number="", name="", associated_experiment=""):
    """Add a petri dish on the grid, number : position on the pile from the ground"""

    if len(grid.object_grid[grid_pos.y_id][grid_pos.x_id]) // 2 < 12:
        if is_not_stack_or_camera(grid, grid_pos):
            grid.add_object(
                [SmallPetriBottom(number=number, associated_name=name, associated_experiment=associated_experiment),
                 SmallPetriTop(number=number, associated_name=name, associated_experiment=associated_experiment)],
                grid_pos)
    else:
        logging.info("Max number of petri dish reached")


def add_pile(grid: Grid, grid_pos: GridPosition, tkinter_window):

    if len(grid.object_grid[grid_pos.y_id][grid_pos.x_id]) // 2 < 2:
        if is_not_stack_or_camera(grid, grid_pos):
            print("launching pile registration")
            # create empty experiment
            ThisExperiment = ExperimentInterface(tkinter_window)
            ThisExperiment.root.mainloop()
            # check all cells to add corresponding piles:
            for row in range(0, 4):
                for column in range(0, 2):
                    grid_pos = GridPosition(column, row)
                    n_experiments = len(ThisExperiment.matrix_experiment_names[row][column])

                    if n_experiments > 0:
                        grid.add_object([PlateHolder(ThisExperiment, num_experiments=n_experiments)], grid_pos)
                        experiment_number = -1
                        marker_number = 1
                        n_petri = len(ThisExperiment.matrix_marker_names[row][column])

                        for index in range(0, n_petri):

                            add_petridish(grid, grid_pos, number=marker_number,
                                          name=ThisExperiment.matrix_marker_names[row][column][index],
                                          associated_experiment=ThisExperiment.matrix_experiment_names[row][column][
                                              experiment_number])

                            marker_number += 1
                            # when the name of the petri dish is 'original', new experiment is found
                            if ThisExperiment.matrix_marker_names[row][column][index] == 'original':
                                experiment_number += 1
                                marker_number = 0
    else:
        logging.info("Max number of Pile reached")

def remove_petridish(grid: Grid, grid_pos: GridPosition):
    """Remove a petri dish on the grid"""

    if len(grid.object_grid[grid_pos.y_id][grid_pos.x_id]) >= 2:
        grid.remove_object(grid.object_grid[grid_pos.y_id][grid_pos.x_id][-2:])
    else:
        logging.info("No petri dish to remove")

def add_plateholder(grid: Grid, grid_pos: GridPosition):
    """"Add a plate holder on the grid"""
    if is_not_stack_or_camera(grid, grid_pos):
        objects = grid.object_grid[grid_pos.y_id][grid_pos.x_id]
        objects = [PlateHolder()] + objects
        grid.object_grid[grid_pos.y_id][grid_pos.x_id] = objects
        grid.height_grid[grid_pos.y_id][grid_pos.x_id] += PlateHolder().height

def remove_plateholder(grid: Grid, grid_pos: GridPosition):
    """Remove a plate holder on the grid"""
    objects = grid.object_grid[grid_pos.y_id][grid_pos.x_id]
    objects = objects[1:]
    grid.object_grid[grid_pos.y_id][grid_pos.x_id] = objects
    grid.height_grid[grid_pos.y_id][grid_pos.x_id] -= PlateHolder().height

def toggle_plateholder(grid: Grid, grid_pos: GridPosition):
    """Toggle the presence of a plate holder on the grid"""

    if len(grid.object_grid[grid_pos.y_id][grid_pos.x_id]) == 0:
        add_plateholder(grid, grid_pos)
    elif grid.object_grid[grid_pos.y_id][grid_pos.x_id][0].name == "Plate Holder":
        remove_plateholder(grid, grid_pos)
    else:
        add_plateholder(grid, grid_pos)

def load_csv_of_experiments(grid: Grid, path):
    with open(path, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')

        for i, row in enumerate(spamreader):
            for j in range(0, 2):
                print("j", j, row[0].split(","))
                text = row[0].split(",")[j]
                if i % 7 == 0:
                    print(i, j, text)
                    if text != '':
                        print("add exp ", text, " at ", i // 7, j)
                        ThisExperiment = Experiment(name=text)
                        plate_holder = PlateHolder(ThisExperiment, associated_name=text)
                        grid.add_object([plate_holder], GridPosition(j, i // 7))
                else:
                    if text != '':
                        print("add marker", text, " at ", i // 7, j)
                        add_petridish(grid, GridPosition(j, i // 7), number=i % 7, name=text)


def mouse_click(event, x, y, flags, param):
    """Mouse callback function that allows the user to interact with the grid"""

    global mouseX, mouseY, left_click, right_click, middle_click
    if event == cv2.EVENT_LBUTTONDOWN:
        left_click = True
    elif event == cv2.EVENT_RBUTTONDOWN:
        right_click = True
    elif event == cv2.EVENT_MBUTTONDOWN:
        middle_click = True

    mouseX, mouseY = x, y


def load_grid(grid: Grid, grid_resolution: int = 100, line_thickness: int = 2, tkinter_window=tk.Tk()) -> Grid:
    """Loads the grid and allows the user to interact with it"""

    global mouseX, mouseY, left_click, right_click, middle_click

    cv2.namedWindow("AutoMate Interface")
    cv2.setMouseCallback("AutoMate Interface", mouse_click)

    Platform = generate_grid_image(grid, grid_resolution, line_thickness)

    while True:
        imshow = Platform.copy()

        draw_grid(grid, imshow, grid_resolution, line_thickness)

        if left_click:
            click_pos = GridPosition(mouseX // (grid_resolution + line_thickness),
                                     mouseY // (grid_resolution + line_thickness))
            add_petridish(grid, click_pos)
            left_click = False
        elif middle_click:
            click_pos = GridPosition(mouseX // (grid_resolution + line_thickness),
                                     mouseY // (grid_resolution + line_thickness))
            remove_petridish(grid, click_pos)
            middle_click = False
        elif right_click:
            click_pos = GridPosition(mouseX // (grid_resolution + line_thickness),
                                     mouseY // (grid_resolution + line_thickness))
            add_pile(grid, click_pos, tkinter_window)
            right_click = False

        cv2.imshow("AutoMate Interface", imshow)
        key = cv2.waitKey(5)

        if key == 13 or key == 27:
            break

    cv2.destroyAllWindows()
    return grid


if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')


    async def main():
        loop = asyncio.get_running_loop()
        executor = ThreadPoolExecutor(max_workers=2)

        grid = Grid(x_max=-800, x_dist=-199, y_max=-620, y_dist=-200)

        grid = await loop.run_in_executor(executor, partial(load_grid, grid))


    asyncio.run(main())
