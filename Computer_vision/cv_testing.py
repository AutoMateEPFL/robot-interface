import cv2
import sys
import os
import platform
if platform.system() == 'Windows':
    sys.path.append(os.path.join(sys.path[0],'..'))
else:
    sys.path.append(r"/Users/Etienne/Documents/GitHub/robot-interface")
from Image_processing.cv_matrix import analyse_matrix, draw_resutls
from Image_processing.cv_orientation import rotateImage, fing_perti_angle

if platform.system() == 'Windows':
    filename = "C:\Users\AutoMate EPFL\Documents\GitHub\robot-interface\Computer_vision\Image_processing\Petri_1.jpeg"
else: 
    filename = "Image_processing/Petri_1.jpeg"
    
image = cv2.imread(filename)

user_angle = 0
auto_rotate = False
positions = [(128, 87), (438, 399)]

while True:

    input = rotateImage(image, user_angle)
    
    # Correction for the rotation of the image
    angle = fing_perti_angle(input)
    if angle is not None:
        output = rotateImage(input, -angle)
    else:
        output = input.copy()
        angle = 0
    
    cv2.putText(input, str(round(angle, 2)), (50,100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2, cv2.LINE_AA)
    cv2.putText(input, str(round(user_angle, 2)), (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2, cv2.LINE_AA)
    
    # Analyse the results 
    matrix = analyse_matrix(output, positions)
    output = draw_resutls(output, positions, matrix)
    
    cv2.imshow('Input', input)
    cv2.imshow('Output', output)

    key = cv2.waitKeyEx(1)
    
    if key == 27:
        break
    elif key == 2490368: # Up
        pass
    elif key == 2621440: # Down
        pass
    elif key == 2424832: # Left
        user_angle +=1
        if user_angle > 180:
            user_angle -= 360
    elif key == 2555904: # Right
        user_angle -=1
        if user_angle < -180:
            user_angle += 360
            
    elif key == ord('r'):
        auto_rotate = True        
    elif key == ord('s'):
        auto_rotate = False
        
    if auto_rotate:
        user_angle -=1
        if user_angle < -180:
            user_angle += 360
            
cv2.destroyAllWindows()
