import numpy as np

class GridPosition:
    def __init__(self, x_id: int, y_id: int, z_id: int) -> None:
        self.x_id = x_id
        self.y_id = y_id
        self.z_id = z_id

class Pickable:
    def __init__(self, name: str, id: int, position: GridPosition, height: float) -> None:
        self.name = name
        self.id = id
        self.position = position
        self. height = height

class Grid:
    def __init__(self, x_max: float, x_num_interval: int, y_max: float, y_num_interval: int, z_max: float, object: Pickable) -> None:
  

        # Create a meshgrid
        self.xx ,self.yy, self.zz = np.mgrid[0:x_max:x_max/x_num_interval, 0:y_max:y_max/y_num_interval, 0:z_max:z_max/object.height]

        def get_position(self, position: GridPosition) -> np.ndarray:
            return np.array([self.xx[position.x_id, position.y_id, position.z_id], self.yy[position.x_id, position.y_id, position.z_id], self.zz[position.x_id, position.y_id, position.z_id]])

    







