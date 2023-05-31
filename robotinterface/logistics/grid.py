import numpy as np

class GridPosition:
    def __init__(self, x_id: int, y_id: int, z_id: int) -> None:
        self.x_id = x_id
        self.y_id = y_id
        self.z_id = z_id

class Grid:
    def __init__(self, x_max: float, x_num_interval: int, y_max: float, y_num_interval: int, z_max: float, object_height: float) -> None:
        # Create a meshgrid

        self.xx, self.yy, self.zz = np.mgrid[0:x_max:x_max / x_num_interval, 0:y_max:y_max / y_num_interval,
                                    0:z_max:-object_height]

        z_num_interval = z_max // object_height

        #self.occupancy = np.zeros((-x_num_interval, -y_num_interval, -z_num_interval))

    def get_coordinates(self, position: GridPosition) -> tuple[float, float, float]:
        return (self.xx[position.x_id, position.y_id, position.z_id], self.yy[position.x_id, position.y_id, position.z_id],
             self.zz[position.x_id, position.y_id, position.z_id])