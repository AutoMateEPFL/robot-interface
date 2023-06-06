import numpy as np

class GridPosition:
    def __init__(self, x_id: int, y_id: int, z_id: int) -> None:
        self.x_id = x_id
        self.y_id = y_id
        self.z_id = z_id

class Grid:
    def __init__(self, x_max: float, x_dist: float, y_max: float, y_dist: float, z_max: float, object_height: float) -> None:
        # Create a meshgrid

        self.xx, self.yy, self.zz = np.mgrid[0:x_max:x_dist, 0:y_max:y_dist, 0:z_max:object_height]
        self.x_num_interval = x_max // x_dist
        self.y_num_interval = y_max // y_dist
        self.z_num_interval = z_max // object_height


        #self.occupancy = np.zeros((-x_num_interval, -y_num_interval, -z_num_interval))

    def get_coordinates(self, position: GridPosition) -> tuple[float, float, float]:
        return (self.xx[position.x_id, position.y_id, position.z_id], self.yy[position.x_id, position.y_id, position.z_id],
             self.zz[position.x_id, position.y_id, position.z_id])

