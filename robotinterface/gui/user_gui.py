import cv2
import numpy as np
from logistics.grid import Grid, GridPosition
from logistics.pickable import *
from robotinterface.gui.experiment_tkinter import *
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import platform
import csv
mouseX, mouseY, left_click, right_click, middle_click = 0, 0, False, False, False

def generate_grid_image(grid: Grid, grid_resolution: int, line_thickness: int):
    """Generates a grid image with the given resolution and line thickness."""

    dark_case = np.ones((grid_resolution, grid_resolution, 3))* np.array([231/255, 212/255, 208/255])
    light_case = np.ones((grid_resolution, grid_resolution, 3))* np.array([244/255, 234/255, 233/255])

    print("size of the grid♟️ : ", grid.x_num_interval, "x", grid.y_num_interval)

    line = dark_case
    for i in range(grid.y_num_interval-1):
        if i%2 == 0:
            line = np.concatenate((line, np.ones((grid_resolution, line_thickness, 3))), axis=1)
            line = np.concatenate((line, light_case), axis=1)
        else:
            line = np.concatenate((line, np.ones((grid_resolution, line_thickness, 3))), axis=1)
            line = np.concatenate((line, dark_case), axis=1)
            
    Imshow = line
    for i in range(grid.x_num_interval-1):
        Imshow = np.concatenate((Imshow, np.ones((line_thickness, Imshow.shape[1], 3))), axis=0)
        Imshow = np.concatenate((Imshow, line), axis=0)
        
    return np.transpose(Imshow, (1, 0, 2))

def draw_plateholder(grid_pos:GridPosition, imshow, grid_resolution, line_thickness):
    """Draws a plateholder on the given grid position."""
    
    if grid_pos.y_id%2 == 0:
        if platform.system() == 'Windows':
            model = cv2.imread("robotinterface\gui\petri_dark.png")
        else :
            model = cv2.imread("../robotinterface/gui/holder_dark.png")
    else:
        if platform.system() == 'Windows':
            model = cv2.imread("robotinterface\gui\holder_light.png")
        else:
            model = cv2.imread("../robotinterface/gui/holder_light.png")
        
    width, height = 70, 70
    model = cv2.resize(model, (width, height))/255

    x = grid_pos.x_id*(grid_resolution+line_thickness)+grid_resolution//2-width//2
    y = grid_pos.y_id*(grid_resolution+line_thickness)+grid_resolution//2-height//2

    x_end = x + width
    y_end = y + height

    imshow[y:y_end, x:x_end] = model


def draw_camera(grid: Grid, imshow, grid_resolution, line_thickness):
    """Draws a camera on the given grid position."""

    grid_pos = grid.find_object(grid.cam)

    if platform.system() == 'Windows':
        camera_image = cv2.imread("robotinterface\gui\camera.png")
    else:
        camera_image = cv2.imread("../robotinterface/gui/camera.png")

    width, height = 90, 90
    model = cv2.resize(camera_image, (width, height)) / 255

    x = grid_pos.x_id * (grid_resolution + line_thickness) + grid_resolution // 2 - width // 2
    y = grid_pos.y_id * (grid_resolution + line_thickness) + grid_resolution // 2 - height // 2

    x_end = x + width
    y_end = y + height

    imshow[y:y_end, x:x_end] = model

def draw_storage(grid: Grid, imshow, grid_resolution, line_thickness):
    """Draws a storage spot  on the given grid position."""

    grid_pos = grid.find_object(grid.stack)

    if platform.system() == 'Windows':
        stack_image = cv2.imread("robotinterface\gui\stack.png")
    else:
        stack_image = cv2.imread("../robotinterface/gui/stack.png")


    width, height = 90, 90
    model = cv2.resize(stack_image, (width, height)) / 255

    x = grid_pos.x_id * (grid_resolution + line_thickness) + grid_resolution // 2 - width // 2
    y = grid_pos.y_id * (grid_resolution + line_thickness) + grid_resolution // 2 - height // 2

    x_end = x + width
    y_end = y + height

    imshow[y:y_end, x:x_end] = model
    
def draw_petri(grid_pos:GridPosition, imshow, grid_resolution, line_thickness):
    """Draws a petri box  on the given grid position."""
    if grid_pos.y_id%2 == 0:
        if platform.system() == 'Windows':
            model = cv2.imread("robotinterface\gui\petri_dark.png")
        else:
            model = cv2.imread("../robotinterface/gui/petri_dark.png")
    else:
        if platform.system() == 'Windows':
            model = cv2.imread("robotinterface\gui\petri_light.png")
        else:
            model = cv2.imread("../robotinterface/gui/petri_light.png")
        
    width, height = 70, 70
    model = cv2.resize(model, (width, height))/255

    x = grid_pos.x_id*(grid_resolution+line_thickness)+grid_resolution//2-width//2
    y = grid_pos.y_id*(grid_resolution+line_thickness)+grid_resolution//2-height//2

    x_end = x + width
    y_end = y + height

    imshow[y:y_end, x:x_end] = model
    
def mark_H(grid_pos:GridPosition, imshow, grid_resolution, line_thickness):
    """Draws H for holder on the given grid position."""
    cv2.putText(imshow, "H", (grid_pos.x_id*(grid_resolution+line_thickness)+5, grid_pos.y_id*(grid_resolution+line_thickness)+17), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 2)
    
def mark_P(grid_pos:GridPosition, num, imshow, grid_resolution, line_thickness):
    cv2.putText(imshow, str(num), ((grid_pos.x_id+1)*(grid_resolution+line_thickness)-20, grid_pos.y_id*(grid_resolution+line_thickness)+17), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 2)
    
def draw_grid(grid: Grid, imshow, grid_resolution, line_thickness):
    """Draw the grid on the imshow"""

    draw_camera(grid,imshow, grid_resolution, line_thickness)
    draw_storage(grid, imshow, grid_resolution, line_thickness)

    for x in range(grid.x_num_interval):
        for y in range(grid.y_num_interval):
            num_petri = 0
            holder = False
            for object in grid.object_grid[y][x]:
                if object.name == "Plate Holder":
                    holder = True
                    draw_plateholder(GridPosition(x, y), imshow, grid_resolution, line_thickness)
                elif object.name == "Small Petri Top":
                    num_petri += 1
            if num_petri > 0:
                draw_petri(GridPosition(x, y), imshow, grid_resolution, line_thickness)
                mark_P(GridPosition(x, y), num_petri, imshow, grid_resolution, line_thickness)
            if holder:
                mark_H(GridPosition(x, y), imshow, grid_resolution, line_thickness)

def add_pertidish(grid: Grid, grid_pos:GridPosition, number= "", name=""):
    """Add a petri dish on the grid, number : position on the pile from the ground"""
    
    if len(grid.object_grid[grid_pos.y_id][grid_pos.x_id]) // 2 < 6:
        if len(grid.object_grid[grid_pos.y_id][grid_pos.x_id])>0 and grid.object_grid[grid_pos.y_id][grid_pos.x_id][0] == grid.cam:
            logging.info("Cannot use photo spot")
        elif len(grid.object_grid[grid_pos.y_id][grid_pos.x_id])>0 and grid.object_grid[grid_pos.y_id][grid_pos.x_id][0] == grid.stack:
            logging.info("Cannot use stack spot")
        else :
            grid.add_object([SmallPetriBottom(number=number,associated_name=name), SmallPetriTop(number=number,associated_name=name)], grid_pos)
    else:
        logging.info("Max number of petri dish reached")


def add_experiment(grid: Grid, grid_pos: GridPosition, tkinter_window):
    """Add an experiment  on the grid"""

    if len(grid.object_grid[grid_pos.y_id][grid_pos.x_id]) // 2 < 2:
        if len(grid.object_grid[grid_pos.y_id][grid_pos.x_id])>0 and grid.object_grid[grid_pos.y_id][grid_pos.x_id][0] == grid.cam:
            logging.info("Cannot use photo spot")
        elif len(grid.object_grid[grid_pos.y_id][grid_pos.x_id])>0 and grid.object_grid[grid_pos.y_id][grid_pos.x_id][0] == grid.stack:
            logging.info("Cannot use stack spot")
        else :
            #create empty experiment
            ThisExperiment = Experiment(name="")
            ThisExperiment.load_external_window(tkinter_window)

            #Setup questions
            ExperimentNameQuestion = Question(ThisExperiment.window.inner, "Name of the experiment ", ThisExperiment.root,setup_question=True)
            for i in range(6):
               ThisExperiment.question_list.append(Question(ThisExperiment.window.inner, "Name of the marker " + str(i + 1),tkinter_window=ThisExperiment.root))

            ThisExperiment.window.mainloop()

            # Updates name of the experiment and names of the markers
            ThisExperiment.update_name(ExperimentNameQuestion.answer)
        for i in range(6):
           ThisExperiment.marker_list.append(ThisExperiment.question_list[i].answer)

        ## Add objects on the grid
        #PlateHolder associated with the experiment
        plate_holder = PlateHolder(ThisExperiment,associated_name=ExperimentNameQuestion.answer)
        grid.add_object([plate_holder], grid_pos)

        # PlateHolder associated with the experiment
        for i in range(6):
            if ThisExperiment.marker_list[i] !='':
                add_pertidish(grid, grid_pos,number=i,name=ThisExperiment.question_list[i].answer)
    else:
        logging.info("Max number of Experiment reached")
        
def remove_pertidish(grid: Grid, grid_pos:GridPosition):
    """Remove a petri dish on the grid"""
    
    if len(grid.object_grid[grid_pos.y_id][grid_pos.x_id]) >= 2:
        grid.remove_object(grid.object_grid[grid_pos.y_id][grid_pos.x_id][-2:])
    else:
        logging.info("No petri dish to remove")
    
def add_plateholder(grid: Grid, grid_pos:GridPosition):
    """"Add a plate holder on the grid"""
    if len(grid.object_grid[grid_pos.y_id][grid_pos.x_id]) > 0 and grid.object_grid[grid_pos.y_id][grid_pos.x_id][
        0] == grid.cam:
        logging.info("Cannot use photo spot")
    elif len(grid.object_grid[grid_pos.y_id][grid_pos.x_id]) > 0 and grid.object_grid[grid_pos.y_id][grid_pos.x_id][
        0] == grid.stack:
        logging.info("Cannot use stack spot")
    else:
        objects = grid.object_grid[grid_pos.y_id][grid_pos.x_id]
        objects = [PlateHolder()] + objects
        grid.object_grid[grid_pos.y_id][grid_pos.x_id] = objects
        grid.height_grid[grid_pos.y_id][grid_pos.x_id] += PlateHolder().height

def remove_plateholder(grid: Grid, grid_pos:GridPosition):
    """Remove a plate holder on the grid"""
    
    objects = grid.object_grid[grid_pos.y_id][grid_pos.x_id]
    objects = objects[1:]
    grid.object_grid[grid_pos.y_id][grid_pos.x_id] = objects 
    grid.height_grid[grid_pos.y_id][grid_pos.x_id] -= PlateHolder().height

def toggle_plateholder(grid: Grid, grid_pos:GridPosition):
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
                print("j",j, row[0].split(",") )
                text = row[0].split(",")[j]
                if i % 7 == 0:
                    print(i, j, text)
                    if text != '':
                        print("add exp ", text, " at ", i//7, j)
                        ThisExperiment = Experiment(name=text)
                        plate_holder = PlateHolder(ThisExperiment, associated_name=text)
                        grid.add_object([plate_holder], GridPosition(j,i//7))
                else:
                    if text != '':
                        print("add marker", text, " at ", i//7, j)
                        add_pertidish(grid, GridPosition(j,i//7), number=i%7, name=text)



def mouse_click(event,x,y,flags,param):
    """Mouse callback function that allows the user to interact with the grid"""
    
    global mouseX,mouseY,left_click,right_click,middle_click
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
        #if grid.object_grid[1][1] != []:
        #    print('NAME',(grid.object_grid[1][1][0].experiment.name))
        #if grid.object_grid[1][1] != []:
        #    print('MARKERS',(grid.object_grid[1][1][0].experiment.marker_list))
        #    print(type(grid.object_grid[1][1][0])==PlateHolder)

        imshow = Platform.copy()
        
        draw_grid(grid, imshow, grid_resolution, line_thickness)
                    
        if left_click:
            click_pos = GridPosition(mouseX//(grid_resolution+line_thickness), mouseY//(grid_resolution+line_thickness))
            add_pertidish(grid, click_pos)
            left_click = False
        elif right_click:
            click_pos = GridPosition(mouseX//(grid_resolution+line_thickness), mouseY//(grid_resolution+line_thickness))
            remove_pertidish(grid, click_pos)
            right_click = False
        elif middle_click:
            click_pos = GridPosition(mouseX//(grid_resolution+line_thickness), mouseY//(grid_resolution+line_thickness))
            #add_plateholder(grid, click_pos)
            add_experiment(grid, click_pos,tkinter_window)
            middle_click = False
    
    
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


    
