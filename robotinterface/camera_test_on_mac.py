# import the opencv library
import cv2
import numpy as np
summary_picture = cv2.imread(r"C:\Users\AutoMate EPFL\Documents\GitHub\robot-interface\images\demo\image_summary.jpeg")
summary_picture = cv2.resize(summary_picture,dsize=(1300,800))
cv2.imshow("",summary_picture)
cv2.waitKey(0)
cv2.destroyAllWindows()