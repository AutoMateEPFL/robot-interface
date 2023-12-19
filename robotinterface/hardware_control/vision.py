from hardware_control.drivers.camera.controller import CameraInterface
from hardware_control.drivers.serial.serial_port_detection import get_cam_index
import platform
my_platform = platform.system()
if my_platform == 'Windows':
    from hardware_control import constants
else :
    import hardware_control.constants
import cv2
import asyncio
import datetime
import os
import logging
import numpy as np
log = logging.getLogger(__name__)

class Vision:
    @classmethod
    async def build(cls, setting: dict[str, any]):
        """
        Asynchronously builds a CV instance.

        Args:
            setting: The settings for the camera.

        Returns:
            Vision: The built CV instance.
        """
        logging.info("Building CV")
        
        if setting["index"] == "auto":
            index = get_cam_index("Logitech BRIO")
        elif setting["index"] == "off":
            index = 0
            logging.warning("Camera is off, need to be implemented")
        else:
            index = setting["index"]
            
        camera = await CameraInterface.build(index)
        logging.info("CV built")
        return cls(camera)

    def __init__(self, camera: CameraInterface):
        """
        Initializes a new instance of the CV class.

        Args:
            camera: The camera object.
        """
        self.camera = camera


    async def save_picture(self, folder_name="", prefix="", suffix="", to_save= True):
        """
        Takes a picture with the camera and saves it to the given path.

        Args:
            path: The path to save the picture to.
        """
        await asyncio.sleep(0.65)
        frame = await self.camera.capture_frame(focus=constants.FOCUS)
        #h,  w = frame.shape[:2]
        #ret = 0.16730785122255515
        #mtx= np.array([[164.20407435,0.0,951.70065218],[  0.0,164.81883753, 555.20676006],[  0.0,0.0,1.0]])
        #dist = np.array([[ 4.63814161e-03, -2.23604220e-04,  6.48638478e-04, -2.35846511e-04, 5.23452299e-06]])
        #newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))
        #frame = cv2.undistort(frame, mtx, dist, None, newcameramtx)

        # Get the current timestamp and convert it to a string
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        #root_folder = "\\nasdcsr.unil.ch/RECHERCHE/FAC/FBM/CIG/avjestic/zygoticfate/D2c/Lab_AutoMate_results"
        root_folder = "C:/Users/AutoMate EPFL/Documents/GitHub/robot-interface"
        if folder_name == "" :
            # Ensure the images directory exists
            os.makedirs("C:/Users/AutoMate EPFL/Documents/GitHub/robot-interface/images/", exist_ok=True)
            # Construct the filename
            filename = f"C:/Users/AutoMate EPFL/Documents/GitHub/robot-interface/images/"+prefix+f'{timestamp}'+suffix+'.jpg'
        else :
            # Ensure the images directory exists
            os.makedirs("C:/Users/AutoMate EPFL/Documents/GitHub/robot-interface/images/"+folder_name, exist_ok=True)
            
            filename =f"C:/Users/AutoMate EPFL/Documents/GitHub/robot-interface/images/"+folder_name+'/'+prefix+f'{timestamp}'+suffix+'.jpg'

        if to_save :
            # Save the frame to a file
            cv2.imwrite(filename, frame)
            logging.info(f"Saved image to {filename}")
        else :
            logging.info("Photo taken but not saved")


    async def shutdown(self):
        """
        Shuts down the camera.
        """
        logging.info("Shutting down camera")
        await self.camera.shutdown()

if __name__ == "__main__":
    async def main():
        cv = await Vision.build()
        await cv.save_picture()
    asyncio.run(main())
