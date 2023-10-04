import cv2
import numpy as np

mouseX,mouseY,left_click,right_click,middle_click = 0,0,False,False,False

#TO DO:
#  Put the detection parameters in a config file

# Setup SimpleBlobDetector parameters.
params = cv2.SimpleBlobDetector_Params()
 
# Change thresholds
params.minThreshold = 50
 
# Filter by Area.
params.filterByArea = True
params.minArea = 70
params.maxArea = 400

# Filter by Circularity
params.filterByCircularity = True
params.minCircularity = 0.4
 
# Filter by Convexity
params.filterByConvexity = False
params.minConvexity = 0.6
 
# Filter by Inertia
params.filterByInertia = False
params.minInertiaRatio = 0.01

colony_detector = cv2.SimpleBlobDetector_create(params)


def draw_clicks(image: np.ndarray, positions: list)->None:
    """
    Draws the clicks on the image

    Args:
        image (np.ndarray): image to draw on
        positions (list): list of positions to draw
    """
    for i in range(len(positions)):
        cv2.circle(image, positions[i], 2, (0,0,255), -1)
        
        
def draw_matrix(image: np.ndarray, positions: list)->None:
    """
    Draws the matrix on the image

    Args:
        image (np.ndarray): image to draw on
        positions (list): list of the two corners of the matrix
    """
    if len(positions) >= 2:
        num_cols: int = 9
        num_rows: int = 9
        
        pos0: tuple = positions[0]
        pos1: tuple = positions[1]
        offset: tuple = ((pos1[0]-pos0[0])/num_cols, (pos1[1]-pos0[1])/num_rows)
        
        for i in range(num_cols):
            for j in range(num_rows):
                if j == 4:
                    continue
                
                pt1: tuple = int(pos0[0]+i*offset[0]), int(pos0[1]+j*offset[1])
                pt2: tuple = int(pos0[0]+(i+1)*offset[0])-1, int(pos0[1]+(j+1)*offset[1])-1
                
                cv2.rectangle(image, pt1, pt2, (255,0,0), 1)
           
           
def analyse_matrix(image: np.ndarray, positions: list)->np.ndarray:
    """
    Analyses the matrix and returns a matrix of 1s and 0s

    Args:
        image (np.ndarray): image to analyse
        positions (list): list of the two corners of the matrix

    Returns:
        matrix (np.ndarray): matrix of 1s and 0s
    """
    global colony_detector
    
    num_cols: int = 9
    num_rows: int = 9
    
    matrix: np.ndarray = np.zeros((num_cols,num_rows))
    
    pos0: tuple = positions[0]
    pos1: tuple = positions[1]
    offset: tuple = ((pos1[0]-pos0[0])/num_cols, (pos1[1]-pos0[1])/num_rows)
    
    bw: np.ndarray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    tr: np.ndarray = cv2.adaptiveThreshold(bw,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 71, -10)
    
    cv2.imshow('tr', tr)
    keypoints: list(cv2.KeyPoint) = colony_detector.detect(tr) 
    
    for keypoint in keypoints:
        if keypoint.pt[0] > pos0[0] and keypoint.pt[0] < pos1[0] and keypoint.pt[1] > pos0[1] and keypoint.pt[1] < pos1[1]:
            matrix[int((keypoint.pt[0]-pos0[0])/offset[0]), int((keypoint.pt[1]-pos0[1])/offset[1])] = 1
            # cv2.circle(image, (int(keypoint.pt[0]), int(keypoint.pt[1])), int(keypoint.size), (255,0,0), 2)
            # cv2.putText(image, str(round(keypoint.size, 2)), (int(keypoint.pt[0]), int(keypoint.pt[1])), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2, cv2.LINE_AA)
            

    return matrix


def draw_resutls(image: np.ndarray, positions: list, matrix: np.ndarray, thickness: int = 2)->np.ndarray:
    """
    Draws the results on the image

    Args:
        image (np.ndarray): image to draw on
        positions (list): list of the two corners of the matrix
        matrix (np.ndarray): results matrix of 1s and 0s
        thickness (int, optional): thickness of the rectangles. Defaults to 2.

    Returns:
        image (np.ndarray): image with the results drawn on it
    """
    
    num_cols: int = 9
    num_rows: int = 9
    
    pos0: tuple = positions[0]
    pos1: tuple = positions[1]
    offset: tuple = ((pos1[0]-pos0[0])/num_cols, (pos1[1]-pos0[1])/num_rows)
    
    for i in range(num_cols):
        for j in range(num_rows):
            if j == 4:
                continue
            
            pt1: tuple = int(pos0[0]+i*offset[0])+thickness, int(pos0[1]+j*offset[1])+thickness
            pt2: tuple = int(pos0[0]+(i+1)*offset[0])-thickness, int(pos0[1]+(j+1)*offset[1])-thickness
            
            if matrix[i,j]: 
                color = (0,255,0) 
            else:
                color = (0,0,255)
                
            cv2.rectangle(image, pt1, pt2, color, thickness)
            
    return image
    

def mouse_click(event,x,y,flags,param):
    global mouseX,mouseY,left_click,right_click,middle_click
    if event == cv2.EVENT_LBUTTONDOWN:
        left_click = True
    elif event == cv2.EVENT_RBUTTONDOWN:
        right_click = True
    elif event == cv2.EVENT_MBUTTONDOWN:
        middle_click = True
        
    mouseX, mouseY = x, y
    
if __name__ == '__main__':
        
    filename = 'Computer_vision\Image_processing\Petri_2.jpeg'
    image = cv2.imread(filename)
    windowname = 'Image matrix'

    cv2.namedWindow(windowname)
    cv2.setMouseCallback(windowname, mouse_click)
    positions = [(118, 92), (425, 404)]
        
    while True:
        
        imshow = image.copy()
                    
        if left_click:
            print(mouseX, mouseY)
            positions.append((mouseX, mouseY))
            left_click = False

        elif right_click:
            positions = []
            right_click = False
            
        if middle_click:
            pass
            middle_click = False
            
        # draw_clicks(imshow, positions)
        matrix = analyse_matrix(imshow, positions)
        imshow = draw_resutls(imshow, positions, matrix)
        
        cv2.imshow(windowname, imshow)
        
        key = cv2.waitKey(5)
        
        if key == 27:
            break