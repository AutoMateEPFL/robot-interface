from typing import Tuple

import numpy as np
from robotinterface.logistics.pickable import Pickable
from robotinterface.logistics.positions import GridPosition, CartesianPosition

class Grid:
    def __init__(self, x_max: float, x_dist: float, y_max: float, y_dist: float) -> None:

        self.xx = np.arange(0, x_max, x_dist)
        self.yy = np.arange(0, y_max, y_dist)

        self.x_num_interval = len(self.xx)
        self.y_num_interval = len(self.yy)

        self.object_grid = [[[] for _ in range(self.x_num_interval)] for _ in range(self.y_num_interval)]
        self.height_grid = [[0.0 for _ in range(self.x_num_interval)] for _ in range(self.y_num_interval)]

    def get_coordinates(self, object: Pickable) -> CartesianPosition:
        position = self.find_object(object)
        z = self.find_stack_position(object, position)
        if z is None:
            raise ValueError("The object is not at the top of the stack")

        x_coord, y_coord = self.get_cooridnates_from_grid(position)

        return CartesianPosition(x_coord, y_coord, z)


    def add_object(self, object_list: list[Pickable], position: GridPosition) -> CartesianPosition:
        old_height = self.height_grid[position.y_id][position.x_id]
        for object in object_list:
            self.object_grid[position.y_id][position.x_id].append(object)
            self.height_grid[position.y_id][position.x_id] += object.height
        x_coord, y_coord = self.get_cooridnates_from_grid(position)
        return CartesianPosition(x_coord, y_coord, old_height)


    def remove_object(self, object_list: list[Pickable]) -> CartesianPosition:
        position = self.find_object(object_list[0])
        for object in object_list:
            self.object_grid[position.y_id][position.x_id].pop()
            self.height_grid[position.y_id][position.x_id] -= object.height

        x_coord, y_coord = self.get_cooridnates_from_grid(position)
        return CartesianPosition(x_coord, y_coord, self.height_grid[position.y_id][position.x_id])

    def find_object(self, object: Pickable) -> GridPosition:
        for y_idx in range(self.y_num_interval):
            for x_idx in range(self.x_num_interval):
                if object in self.object_grid[y_idx][x_idx]:
                    return GridPosition(x_idx, y_idx)

    def find_stack_position(self, object: Pickable, position: GridPosition) -> None | float:
        if self.object_grid[position.y_id][position.x_id][-1] is object:
            return self.height_grid[position.y_id][position.x_id]
        else:
            return None

    def get_cooridnates_from_grid(self, position: GridPosition) -> tuple[float, float]:
        return self.xx[position.x_id], self.yy[position.y_id]



