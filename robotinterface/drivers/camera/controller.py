import asyncio
import cv2
from concurrent.futures import ThreadPoolExecutor

class CameraInterface:

    def __init__(self):
        self.cap = cv2.VideoCapture()
        fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
        self.cap.open(cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FOURCC, fourcc)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        self.cap.set(cv2.CAP_PROP_FPS, 60)
        # Check if camera opened successfully
        if not self.cap.isOpened():
            raise IOError("Cannot open camera")
        self.executor = ThreadPoolExecutor(max_workers=1)

    async def capture_frame(self):
        loop = asyncio.get_running_loop()
        ret, frame = await loop.run_in_executor(self.executor, self.cap.read)
        return frame

    async def show_video(self):
        """
        Continuously get frames and display them.
        """
        while True:
            frame = await self.capture_frame()
            cv2.imshow('frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        await self.shutdown()


    async def shutdown(self):
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(self.executor, self.cap.release)



if __name__ == "__main__":
    camera = CameraInterface()
    asyncio.run(camera.show_video())





