import cv2
import numpy as np
from robotinterface.logistics.grid import Grid, GridPosition
from robotinterface.logistics.pickable import *
import logging

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S')

mouseX,mouseY,left_click,right_click,middle_click = 0,0,False,False,False

grid = Grid(x_max=-800, x_dist=-200, y_max=-620, y_dist=-120)

end_pos = GridPosition(0, 0)
zero_pos = GridPosition(0, 1)
one_pos = GridPosition(1, 1)
two_pos = GridPosition(2, 2)

plateHolders = list()
for i in range(4):
    print(i)
    plateHolders.append(PlateHolder())

Objects = list()
for i in range(15):
    Objects.append(SmallPetriBottom())
    Objects.append(SmallPetriTop())
    

grid.add_object([plateHolders[0]] + Objects[:5*2], zero_pos)
grid.add_object([plateHolders[1]] + Objects[5*2:10*2], one_pos)
grid.add_object([plateHolders[2]] + Objects[10*2:15*2], two_pos)

grid.add_object([SmallPetriBottom(), SmallPetriTop()], GridPosition(2, 1))

grid.add_object([plateHolders[3]], end_pos)

grid_resolution = 100
line_thickness = 2

dark_case = np.ones((grid_resolution, grid_resolution, 3))* np.array([231/255, 212/255, 208/255])
light_case = np.ones((grid_resolution, grid_resolution, 3))* np.array([244/255, 234/255, 233/255])

print("size of the grid: ", grid.x_num_interval, "x", grid.y_num_interval, "y" )

line = dark_case
for i in range(grid.y_num_interval-1):
    if i%2 == 0:
        line = np.concatenate((line, np.ones((grid_resolution, line_thickness, 3))), axis=1)
        line = np.concatenate((line, light_case), axis=1)
    else:
        line = np.concatenate((line, np.ones((grid_resolution, line_thickness, 3))), axis=1)
        line = np.concatenate((line, dark_case), axis=1)
        
Platform = line
for i in range(grid.x_num_interval-1):
    Platform = np.concatenate((Platform, np.ones((line_thickness, Platform.shape[1], 3))), axis=0)
    Platform = np.concatenate((Platform, line), axis=0)
    
Platform = np.transpose(Platform, (1, 0, 2))

def draw_plateholder(grid_pos:GridPosition, imshow):
    if grid_pos.y_id%2 == 0:
        model = cv2.imread("robotinterface\holder_dark.png")
    else:
        model = cv2.imread("robotinterface\holder_light.png")
        
    width, height = 70, 70
    model = cv2.resize(model, (width, height))/255

    x = grid_pos.x_id*(grid_resolution+line_thickness)+grid_resolution//2-width//2
    y = grid_pos.y_id*(grid_resolution+line_thickness)+grid_resolution//2-height//2

    x_end = x + width
    y_end = y + height

    imshow[y:y_end, x:x_end] = model
    
def draw_petri(grid_pos:GridPosition, imshow):
    if grid_pos.y_id%2 == 0:
        model = cv2.imread("robotinterface\petri_dark.png")
    else:
        model = cv2.imread("robotinterface\petri_light.png")
        
    width, height = 70, 70
    model = cv2.resize(model, (width, height))/255

    x = grid_pos.x_id*(grid_resolution+line_thickness)+grid_resolution//2-width//2
    y = grid_pos.y_id*(grid_resolution+line_thickness)+grid_resolution//2-height//2

    x_end = x + width
    y_end = y + height

    imshow[y:y_end, x:x_end] = model
    
def mark_H(grid_pos:GridPosition, imshow):
    cv2.putText(imshow, "H", (grid_pos.x_id*(grid_resolution+line_thickness)+5, grid_pos.y_id*(grid_resolution+line_thickness)+17), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 2)
    
def mark_P(grid_pos:GridPosition, num, imshow):
    cv2.putText(imshow, str(num), ((grid_pos.x_id+1)*(grid_resolution+line_thickness)-20, grid_pos.y_id*(grid_resolution+line_thickness)+17), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 2)
    
def draw_grid(imshow):
    for x in range(grid.x_num_interval):
        for y in range(grid.y_num_interval):
            num_petri = 0
            holder = False
            for object in grid.object_grid[y][x]:
                if object.name == "Plate Holder":
                    holder = True
                    draw_plateholder(GridPosition(x, y), imshow)
                elif object.name == "Small Petri Bottom":
                    num_petri += 1
            if num_petri > 0:
                draw_petri(GridPosition(x, y), imshow)
                mark_P(GridPosition(x, y), num_petri, imshow)
            if holder:
                mark_H(GridPosition(x, y), imshow)
    
def add_pertidish(grid_pos:GridPosition):
    if len(grid.object_grid[grid_pos.y_id][grid_pos.x_id]) // 2 < 6:
        grid.add_object([SmallPetriBottom(), SmallPetriTop()], grid_pos)
    else:
        logging.info("Max number of petri dish reached")
        
def remove_pertidish(grid_pos:GridPosition):
    if len(grid.object_grid[grid_pos.y_id][grid_pos.x_id]) >= 2:
        grid.remove_object(grid.object_grid[grid_pos.y_id][grid_pos.x_id][-2:])
    else:
        logging.info("No petri dish to remove")
    
def add_plateholder(grid_pos:GridPosition):
    objects = grid.object_grid[grid_pos.y_id][grid_pos.x_id]
    objects = [PlateHolder()] + objects	
    grid.object_grid[grid_pos.y_id][grid_pos.x_id] = objects 

def remove_plateholder(grid_pos:GridPosition):
    objects = grid.object_grid[grid_pos.y_id][grid_pos.x_id]
    objects = objects[1:]
    grid.object_grid[grid_pos.y_id][grid_pos.x_id] = objects 

def toggle_plateholder(grid_pos:GridPosition):
    if len(grid.object_grid[grid_pos.y_id][grid_pos.x_id]) == 0:
        add_plateholder(grid_pos)   
    elif grid.object_grid[click_pos.y_id][click_pos.x_id][0].name == "Plate Holder":
        remove_plateholder(grid_pos)
    else:
        add_plateholder(grid_pos)
            
            
def mouse_click(event,x,y,flags,param):
    global mouseX,mouseY,left_click,right_click,middle_click
    if event == cv2.EVENT_LBUTTONDOWN:
        left_click = True
    elif event == cv2.EVENT_RBUTTONDOWN:
        right_click = True
    elif event == cv2.EVENT_MBUTTONDOWN:
        middle_click = True
        
    mouseX, mouseY = x, y
    
cv2.namedWindow("Auto-One")
cv2.setMouseCallback("Auto-One", mouse_click)
    
    
while True:
    
    imshow = Platform.copy()
    
    draw_grid(imshow)
                
    if left_click:
        click_pos = GridPosition(mouseX//(grid_resolution+line_thickness), mouseY//(grid_resolution+line_thickness))
        add_pertidish(click_pos)
        left_click = False
    elif right_click:
        click_pos = GridPosition(mouseX//(grid_resolution+line_thickness), mouseY//(grid_resolution+line_thickness))
        remove_pertidish(click_pos)
        right_click = False
    if middle_click:
        click_pos = GridPosition(mouseX//(grid_resolution+line_thickness), mouseY//(grid_resolution+line_thickness))
        toggle_plateholder(click_pos)           
        middle_click = False
    
    
    cv2.imshow("Auto-One", imshow)
    key = cv2.waitKey(5)
                
        
                
    
    # draw_petri(GridPosition(1, 1), imshow)
    # draw_plateholder(GridPosition(1, 1), imshow)
    
    # cv2.rectangle(imshow, (0, 0), (100, 100), 0, -1)
    
    
    if key == 13 or key == 27:
        break
    
# dark_case = np.ones((grid_resolution*4, grid_resolution*4, 3))* np.array([231/255, 212/255, 208/255])
# light_case = np.ones((grid_resolution*4, grid_resolution*4, 3))* np.array([244/255, 234/255, 233/255])

# cv2.circle(dark_case, (grid_resolution*2, grid_resolution*2), 180, (0,0,0), -1)
# cv2.circle(light_case, (grid_resolution*2, grid_resolution*2), 180, (0,0,0), -1)

# dark_case = cv2.GaussianBlur(dark_case, (7, 7), 0)
# light_case = cv2.GaussianBlur(light_case, (7, 7), 0)

# cv2.imwrite("robotinterface\holder_dark.png", dark_case*255)
# cv2.imwrite("robotinterface\holder_light.png", light_case*255)