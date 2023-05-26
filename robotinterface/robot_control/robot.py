from robotinterface.robot_control.connection import Connection
import logging

log = logging.getLogger(__name__)

class robot:

    def __init__(self, dyna_connection: Connection, grbl_connection: Connection) -> None:
        self.dyna = dyna_connection
        self.grbl = grbl_connection

    