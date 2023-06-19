import logging
from robotinterface.drivers.grbl.controller import GrblDriver

log = logging.getLogger(__name__)

class Platform(GrblDriver):

    @classmethod
    async def build(cls, setting: dict[str, any]):

        logging.info("Building Platform")
        grbl = await super(Platform, cls).build(setting["port"], setting["bauderate"])

        await grbl.home()
        # Set the origin of the G55 coordinate system to the workplane and shift so the camera still could
        # still take a picture of the origin
        await grbl.send_command(f"G10 L2 P2 X-{setting['x_offset_camera']} Y0 Z{setting['z_offset']}")

        # Set the origin of the G56 coordinate system such that the camera can take a picture of the origin when
        # moving to X0 Y0 Z0
        await grbl.send_command(f"G10 L2 P3 X0 Y0 Z{setting['z_offset_camera']}")
        await grbl.send_command("G55")
        logging.info("Platform built")

        return grbl

