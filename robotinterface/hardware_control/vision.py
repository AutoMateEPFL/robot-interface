from robotinterface.hardware_control.drivers.camera.controller import CameraInterface
from robotinterface.hardware_control.drivers.serial.serial_port_detection import get_cam_index
import cv2
import asyncio
import datetime
import os
import logging

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


    async def save_picture(self):
        """
        Takes a picture with the camera and saves it to the given path.

        Args:
            path: The path to save the picture to.
        """
        frame = await self.camera.capture_frame()

        # Get the current timestamp and convert it to a string
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

        # Ensure the images directory exists
        os.makedirs('images', exist_ok=True)

        # Construct the filename
        filename = f'images/{timestamp}.jpg'

        # Save the frame to a file
        cv2.imwrite(filename, frame)
        logging.info(f"Saved image to {filename}")


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