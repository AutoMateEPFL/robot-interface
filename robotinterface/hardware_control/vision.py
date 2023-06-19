from robotinterface.drivers.camera.controller import CameraInterface
import cv2
import asyncio
import datetime
import os


class Vision:
    @classmethod
    async def build(cls):
        """
        Asynchronously builds a CV instance.

        Args:
            setting: The settings for the camera.

        Returns:
            Vision: The built CV instance.
        """
        camera = await CameraInterface.build()
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

if __name__ == "__main__":
    async def main():
        cv = await Vision.build()
        await cv.save_picture()
    asyncio.run(main())