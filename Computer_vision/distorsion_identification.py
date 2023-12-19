import cv2
import numpy as np
import glob
import cv2
import os

if False:
    # Set the path to the folder where images will be saved
    save_folder = '/Users/Etienne/Documents/GitHub/robot-interface/images/'

    # Create the save folder if it doesn't exist
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    # Initialize the camera
    cap = cv2.VideoCapture(0)  # Use 0 for the default camera, change it if you have multiple cameras

    # Variables for image counter
    img_counter = 0

    while True:
        ret, frame = cap.read()

        cv2.imshow("Press spacebar to capture", frame)

        # Wait for key event
        key = cv2.waitKey(1)

        # Capture image when spacebar is pressed
        if key == 32:  # Spacebar key code
            img_name = "calibration_image_{}.jpg".format(img_counter)
            img_path = os.path.join(save_folder, img_name)
            cv2.imwrite(img_path, frame)
            print("{} written!".format(img_name))
            img_counter += 1

        # Break the loop if 'ESC' key is pressed
        elif key == 27:
            break

    # Release the camera and close all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()


# Size of the chessboard
chessboard_size = (3, 5)

# Create object points for the chessboard
objp = np.zeros((np.prod(chessboard_size), 3), dtype=np.float32)
objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2)

# Arrays to store object points and image points from all images
objpoints = []  # 3D points in real world space
imgpoints = []  # 2D points in image plane

# Load images taken with the camera
# Replace 'path/to/images/*.jpg' with the path to your images
images = glob.glob("C:/Users/AutoMate EPFL/Documents/GitHub/robot-interface/images/*.jpg")
print('images',images)
for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Find the chessboard corners
    ret, corners = cv2.findChessboardCorners(gray, chessboard_size, None)
    print(corners)

    # If found, add object points, image points (after refining them)
    if ret:
        print('found')
        objpoints.append(objp)

        corners2 = cv2.cornerSubPix(
            gray, corners, (11, 11), (-1, -1), criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        )
        imgpoints.append(corners2)

        # Draw and display the corners
        img = cv2.drawChessboardCorners(img, chessboard_size, corners2, ret)
        cv2.imshow('img', img)
        cv2.waitKey(500)

cv2.destroyAllWindows()

# Calibrate the camera
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
print("ret",ret)
print("mtx",mtx)
print("dist",dist)

# Save the calibration parameters to a file (optional)
np.savez('calibration.npz', mtx=mtx, dist=dist, rvecs=rvecs, tvecs=tvecs)

# Print the distortion parameters
print("Camera matrix:\n", mtx)
print("\nDistortion coefficients:\n", dist)
