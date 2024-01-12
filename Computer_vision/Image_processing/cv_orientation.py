import cv2
import numpy as np
import logging

def rotateImage(image: np.ndarray, angle: float)->np.ndarray:
    """
    Rotates an image (angle in degrees) and expands image to avoid cropping

    Args:
        image (np.ndarray): image to be rotated
        angle (float): angle of rotation in degrees

    Returns:
        np.ndarray: image rotated by the angle with zero padding
    """
    row,col = image.shape[0:2]
    center=tuple(np.array([col,row])/2)
    rot_mat = cv2.getRotationMatrix2D(center,angle,1.0)
    new_image = cv2.warpAffine(image, rot_mat, (col,row), image.shape[1::-1], flags=cv2.INTER_LINEAR)
    
    return new_image

def projection(pt_to_project: np.ndarray, vect: np.ndarray, pt:np.ndarray)->np.ndarray:
    """
    Project a point on a line

    Args:
        pt_to_project (np.ndarray): point to project
        vect (np.ndarray): vector of the line
        pt (np.ndarray): point on the line

    Returns:
        np.ndarray: projected point
    """
    vect = vect/np.linalg.norm(vect)
    proj = np.dot(pt_to_project-pt, vect)*vect + pt
    
    return proj

def find_petri_angle_using_line(image: np.ndarray)->float:
    """
    Finds the angle of the petri dish using the Hough transform on the Canny edge detection

    Args:
        image (np.ndarray): image of the petri dish

    Returns:
        float: angle of the petri dish in degrees if found, None otherwise
    """
    src = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    dst = cv2.Canny(src, 50, 200, None, 3)
    
    mask = np.zeros(dst.shape[0:2], dtype='uint8')
    center_coordinates = (int(mask.shape[1]/2), int(mask.shape[0]/2))
    radius = (dst.shape[1])//2
    mask = cv2.circle(mask, center_coordinates, radius, 255, -1)
    dst = cv2.bitwise_and(dst, dst, mask=mask)

    cdst = np.copy(cv2.cvtColor(src, cv2.COLOR_GRAY2BGR))

    lines = cv2.HoughLines(dst, 1, np.pi / 720, 150, None, 0, 0)
    
    if lines is not None:
        angle = []
        for i in range(0, min(2, len(lines))):
            rho = lines[i][0][0]   
            theta = lines[i][0][1]
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a * rho
            y0 = b * rho
            pt = np.array([int(x0), int(y0)])
            center = np.array([cdst.shape[0]//2, cdst.shape[1]//2])
            proj = projection(center, (-b, a), pt)
        
            angle.append(180/np.pi*np.arctan2(center[1]-proj[1], center[0]-proj[0]))

        return -np.mean(angle)
    else:
        logging.info('No lines found')
        return None


def detect_sticker(cropped_input):
    #cropped_input = cv2.cvtColor(cropped_input, cv2.COLOR_BGR2RGB)

    row, col = cropped_input.shape[0:2]
    center = tuple(np.array([col, row]) / 2)
    intermediate =  cv2.cvtColor(cropped_input, cv2.COLOR_BGR2RGB)
    bw: np.ndarray = cv2.cvtColor(intermediate, cv2.COLOR_BGR2GRAY)
#    gray = cv2.adaptiveThreshold(bw, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 255, -10)

    _, binary_image = cv2.threshold(bw, 190, 255, cv2.THRESH_BINARY)
    edges = cv2.Canny(binary_image, 100, 255)
    gray = edges

    # Blur using 3 * 3 kernel.
    gray_blurred = cv2.blur(gray, (2, 2))

    # Apply Hough transform on the blurred image.
    detected_circles = cv2.HoughCircles(gray_blurred,
                                        cv2.HOUGH_GRADIENT, 1, 20, param1=50,
                                        param2=28, minRadius=45, maxRadius=120)
    angle = 0
    num_of_sticker = 0
    list_of_angles = []
    try :
        for pt in detected_circles[0, :]:
            a, b, r = pt[0], pt[1], pt[2]
            #print("a", a, "b", b, "r", r)
            # Draw the circumference of the circle.
            if r <= 58.2 and r >= 47:
                num_of_sticker += 1
                # print("a", a, "b", b, "r", r)
                cv2.circle(cropped_input, (int(a), int(b)), int(r), (0, 255, 0), 2)

                # Draw a small circle (of radius 1) to show the center.
                cv2.circle(cropped_input, (int(a), int(b)), 1, (0, 0, 255), 3)
                angle = np.arctan2((b - center[1]), (a - center[0])) * 180 / np.pi
                list_of_angles.append(angle)
    except:
        print("NO STICKER DETECTED, ANGLE=0")
        pass

    return 180 - angle
    
