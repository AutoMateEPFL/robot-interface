import asyncio
import cv2
import logging
from concurrent.futures import ThreadPoolExecutor
from functools import partial

log = logging.getLogger(__name__)

class CameraInterface:
    @classmethod
    async def build(cls, index:int = 0):
        """
        Asynchronously builds a CameraInterface instance.

        Returns:
            CameraInterface: The built CameraInterface instance.
        """
        self = cls()
        self.focus = 30
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.loop = asyncio.get_running_loop()
        self.cap = await self.loop.run_in_executor(self.executor, partial(cv2.VideoCapture, index, cv2.CAP_DSHOW))
        await self.loop.run_in_executor(self.executor, partial(self.cap.set, cv2.CAP_PROP_FRAME_WIDTH, 1920))
        await self.loop.run_in_executor(self.executor, partial(self.cap.set, cv2.CAP_PROP_FRAME_HEIGHT, 1080))
        await self.loop.run_in_executor(self.executor, partial(self.cap.set, cv2.CAP_PROP_FPS, 60))
        # self.cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
        # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 4096)
        # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 2160)
        # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
        # await self.loop.run_in_executor(self.executor, partial(self.cap.open, cv2.CAP_DSHOW))

        # Set the fourcc (codec used for compression), frame size and FPS
        # self.cap.set(cv2.CAP_PROP_FOURCC, fourcc)
        # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        # self.cap.set(cv2.CAP_PROP_FPS, 60)

        # Check if camera opened successfully
        if not self.cap.isOpened():
            raise IOError("Cannot open camera")

        return self

    async def capture_frame(self, focus=None, discarded_frames=2):
        """
        Capture a frame from the camera asynchronously.

        Returns: frame: The captured frame.
                 discarded_frames: The number of frames to discard before returning the
                 frame. As otherwise the image could be black.
        """
        logging.debug("Camera capturing frame")
        if focus is not None:
            self.cap.set(cv2.CAP_PROP_FOCUS, self.focus)
        for _ in range(discarded_frames):
            ret, frame = await self.loop.run_in_executor(self.executor, self.cap.read)
            self.focus += 5
            logging.info(f"focus {self.focus}")
        return frame

    async def show_video(self):
        """
        Continuously get frames and display them.
        """
        while True:
            frame = await self.capture_frame()
            cv2.imshow('frame', frame)

            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        await self.shutdown()

    async def shutdown(self):
        """
        Close the VideoCapture object asynchronously.
        """
        logging.debug("Camera shutting down")
        await self.loop.run_in_executor(self.executor, self.cap.release)


if __name__ == "__main__":
    async def main():
        # Create a CameraInterface and show video from the camera
        camera = await CameraInterface.build()
        await camera.show_video()


    # Run the main function
    asyncio.run(main())
