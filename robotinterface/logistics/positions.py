class GridPosition:
    def __init__(self, x_id: int, y_id: int) -> None:
        self.x_id = x_id
        self.y_id = y_id

    def __eq__(self, other):
        if not isinstance(other, GridPosition):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.x_id == other.x_id and self.y_id == other.y_id


class CartesianPosition:
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

    def __eq__(self, other):
        if not isinstance(other, CartesianPosition):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.x == other.x and self.y == other.y and self.z == self.z