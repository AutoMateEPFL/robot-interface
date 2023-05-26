import logging
import asyncio

from robotinterface.drivers.grbl.controller import GrblDriver


logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

async def main():
    grbl_driver = await GrblDriver.build("/dev/ttyUSB0", 115200)
    await grbl_driver.home()
    await grbl_driver.move(-0, -0, -498.93, 500)


asyncio.run(main())
