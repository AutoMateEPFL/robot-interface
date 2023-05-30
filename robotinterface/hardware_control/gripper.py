from robotinterface.drivers.dynamixel.controller import Dynamixel
import  robotinterface.hardware_control.constants 

import logging

log = logging.getLogger(__name__)

class Gripper():
    def __init__(self, id_rotate: int, id_grip: int, connection: Dynamixel) -> None:
        self.id_rotate = id_rotate
        self.id_grip = id_grip
        self.connection = connection

    def open(self):
        log.debug("opening gripper")
        self.connection.write_pwm(500, self.id_grip)

    
    def close(self):
        log.debug("closing gripper")
        self.connection.write_pwm(constants.pwm, self.id_grip)

    def rotate(self):

