import asyncio
import cv2
import logging
from concurrent.futures import ThreadPoolExecutor
from functools import partial

async def build():

    executor = ThreadPoolExecutor(max_workers=2)
    loop = asyncio.get_running_loop()
    # cap = cv2.VideoCapture(1)
    # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 4096)
    # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 2160)
    # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    # fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
    # await loop.run_in_executor(executor, partial(cap.open, cv2.CAP_DSHOW))
    index = 1    cap = await loop.run_in_executor(executor, partial(cv2.VideoCapture, index, cv2.CAP_DSHOW))
    await loop.run_in_executor(executor, partial(cap.set, cv2.CAP_PROP_FRAME_WIDTH, 1920))
    await loop.run_in_executor(executor, partial(cap.set, cv2.CAP_PROP_FRAME_HEIGHT, 1080))

    return cap
    
        
cap = asyncio.run(build())

while True:
    
    frame = cap.read()[1]
    
    cv2.imshow("frame", frame)
    
    key = cv2.waitKey(1)
    
    if key == ord("q"):
        break
    