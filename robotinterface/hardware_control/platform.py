import logging
from robotinterface.hardware_control.drivers.grbl.controller import GrblDriver
from robotinterface.hardware_control.drivers.serial.serial_port_detection import get_com_port

log = logging.getLogger(__name__)

class Platform(GrblDriver):

    @classmethod
    async def build(cls, setting: dict[str, any], tools_settings: list[dict[str, any]]):

        logging.info("Building Platform")
        
        if setting["port"] == "auto":
            port = get_com_port("0403", "6001")
        else:
            port = setting["port"]
            
        grbl = await super(Platform, cls).build(port, setting["bauderate"])

        await grbl.home()
    
        # Offset configurations
        for tool in tools_settings:
            await grbl.configure_space(tool['id'], tool['x_offset'], tool['y_offset'], tool['z_offset'])
        
        await grbl.set_space(1)
        logging.info("Platform built")

        return grbl

