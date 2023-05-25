import logging

log = logging.getLogger(__name__)

class Connection:

    def __init__(self, path: str, bauderate: int) -> None:
        self.path = path
        

    @staticmethod
    def deviceAvailable(path: str) -> bool:
        pass

        