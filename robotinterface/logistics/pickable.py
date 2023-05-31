from robotinterface.logistics.grid import GridPosition


class Pickable:
    def __init__(self, name: str, id: int, position: GridPosition, height: float) -> None:
        self.name = name
        self.id = id
        self.position = position
        self.height = height
