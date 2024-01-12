import cv2
import numpy as np

original = cv2.imread("/Users/Etienne/Documents/GitHub/robot-interface/images/2/20231026135243_c.jpg", cv2.IMREAD_GRAYSCALE)
retval, image = cv2.threshold(original, 50, 255, cv2.THRESH_BINARY)

el = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
image = cv2.dilate(image, el, iterations=6)

cv2.imwrite("dilated.png", image)

contours, hierarchy = cv2.findContours(
    image,
    cv2.CV_RETR_LIST,
    cv2.CV_CHAIN_APPROX_SIMPLE
)

drawing = cv2.imread("test.jpg")

centers = []
radii = []
for contour in contours:
    area = cv2.contourArea(contour)

    # there is one contour that contains all others, filter it out
    if area > 500:
        continue

    br = cv2.boundingRect(contour)
    radii.append(br[2])

    m = cv2.moments(contour)
    center = (int(m['m10'] / m['m00']), int(m['m01'] / m['m00']))
    centers.append(center)

print("There are {} circles".format(len(centers)))

radius = int(np.average(radii)) + 5

for center in centers:
    cv2.circle(drawing, center, 3, (255, 0, 0), -1)
    cv2.circle(drawing, center, radius, (0, 255, 0), 1)

cv2.imwrite("drawing.png", drawing)
