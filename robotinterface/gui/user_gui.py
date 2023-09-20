import cv2
import numpy as np
from logistics.grid import Grid, GridPosition
from logistics.pickable import *
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial

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
        model = cv2.imread("robotinterface\gui\holder_dark.png")
    else:
        model = cv2.imread("robotinterface\gui\holder_light.png")
        
    width, height = 70, 70
    model = cv2.resize(model, (width, height))/255

    x = grid_pos.x_id*(grid_resolution+line_thickness)+grid_resolution//2-width//2
    y = grid_pos.y_id*(grid_resolution+line_thickness)+grid_resolution//2-height//2

    x_end = x + width
    y_end = y + height

    imshow[y:y_end, x:x_end] = model
    
def draw_petri(grid_pos:GridPosition, imshow, grid_resolution, line_thickness):
    if grid_pos.y_id%2 == 0:
        model = cv2.imread("robotinterface\gui\petri_dark.png")
    else:
        model = cv2.imread("robotinterface\gui\petri_light.png")
        
    width, height = 70, 70
    model = cv2.resize(model, (width, height))/255

    x = grid_pos.x_id*(grid_resolution+line_thickness)+grid_resolution//2-width//2
    y = grid_pos.y_id*(grid_resolution+line_thickness)+grid_resolution//2-height//2

    x_end = x + width
    y_end = y + height

    imshow[y:y_end, x:x_end] = model
    
def mark_H(grid_pos:GridPosition, imshow, grid_resolution, line_thickness):
    cv2.putText(imshow, "H", (grid_pos.x_id*(grid_resolution+line_thickness)+5, grid_pos.y_id*(grid_resolution+line_thickness)+17), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 2)
    
def mark_P(grid_pos:GridPosition, num, imshow, grid_resolution, line_thickness):
    cv2.putText(imshow, str(num), ((grid_pos.x_id+1)*(grid_resolution+line_thickness)-20, grid_pos.y_id*(grid_resolution+line_thickness)+17), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 2)
    
def draw_grid(grid: Grid, imshow, grid_resolution, line_thickness):
    """Draw the grid on the imshow"""
    
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
    
def add_pertidish(grid: Grid, grid_pos:GridPosition):
    """Add a petri dish on the grid"""
    
    if len(grid.object_grid[grid_pos.y_id][grid_pos.x_id]) // 2 < 6:
        grid.add_object([SmallPetriBottom(), SmallPetriTop()], grid_pos)
    else:
        logging.info("Max number of petri dish reached")
        
def remove_pertidish(grid: Grid, grid_pos:GridPosition):
    """Remove a petri dish on the grid"""
    
    if len(grid.object_grid[grid_pos.y_id][grid_pos.x_id]) >= 2:
        grid.remove_object(grid.object_grid[grid_pos.y_id][grid_pos.x_id][-2:])
    else:
        logging.info("No petri dish to remove")
    
def add_plateholder(grid: Grid, grid_pos:GridPosition):
    """"Add a plate holder on the grid"""
    
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
      
    
def load_grid(grid: Grid, grid_resolution: int = 100, line_thickness: int = 2) -> Grid:
    """Loads the grid and allows the user to interact with it"""
    
    global mouseX,mouseY,left_click,right_click,middle_click
    
    cv2.namedWindow("Auto-One")
    cv2.setMouseCallback("Auto-One", mouse_click)
    
    Platform = generate_grid_image(grid, grid_resolution, line_thickness)
    
    while True:
        
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
            toggle_plateholder(grid, click_pos)           
            middle_click = False
    
    
        cv2.imshow("Auto-One", imshow)
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
    
