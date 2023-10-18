from typing import Tuple
import logging
import numpy as np
from logistics.pickable import Pickable
from logistics.non_pickable import *
from logistics.positions import GridPosition, CartesianPosition

log = logging.getLogger(__name__)

class Grid:
    """
    This class represents a 2D grid inside the workspace of the robot. At each of the grid positions objects can be stacked
    on top of each other. For example, petri dishes can be stacked. To represent this, at each grid position, a list stores
    all the objects that are stacked at this position. A second grid keeps track of the current height of the stack.

    Args:
        x_max: The maximal extension of the grid in the x direction.
        x_dist: The distance between each grid position in the x direction.
        y_max: The maximal extension of the grid in the y direction.
        y_dist: The distance between each grid position in the y direction.
    """

    def __init__(self, x_max: float, x_dist: float, y_max: float, y_dist: float) -> None:
        """
        Initializes a new instance of the GridPosition class.

        Args:
            x_max: The maximal extension of the grid in the x direction.
            x_dist: The distance between each grid position in the x direction.
            y_max: The maximal extension of the grid in the y direction.
            y_dist: The distance between each grid position in the y direction.
        """
        self.xx = np.arange(0, x_max, x_dist)
        self.yy = np.arange(0, y_max, y_dist)

        self.x_num_interval = len(self.xx)
        self.y_num_interval = len(self.yy)

        self.object_grid = [[[] for _ in range(self.x_num_interval)] for _ in range(self.y_num_interval)]
        self.height_grid = [[0.0 for _ in range(self.x_num_interval)] for _ in range(self.y_num_interval)]

    def get_coordinates(self, obj: Pickable) -> CartesianPosition:
        """
        Gets the 3D Cartesian coordinates of an object that is placed on the grid.

        Args:
            obj: An object that is placed on the 2D grid.

        Returns:
            The position of that object in the workspace of the robot.
        """
        position = self.find_object(obj)
        z = self.find_stack_position(obj, position)
        if z is None:
            raise ValueError("The object is not at the top of the stack")

        x_coord, y_coord = self.get_coordinates_from_grid(position)

        return CartesianPosition(x_coord, y_coord, z)

    def add_object(self, obj_list: list[Pickable], position: GridPosition) -> CartesianPosition:
        """
        Adds a list of objects to a specific position on the grid. The first object of the list will be at the lowest position

        Args:
            obj_list (list[Pickable]): The list of objects to be added.
            position (GridPosition): The position on the grid where the objects should be added.

        Returns:
            The 3D Cartesian coordinates of the updated position after adding the objects.
        """
        old_height = self.height_grid[position.y_id][position.x_id]
        for obj in obj_list:
            self.object_grid[position.y_id][position.x_id].append(obj)
            self.height_grid[position.y_id][position.x_id] += obj.height
            logging.info(f"Added the {obj.name} with id {obj.id} to the grid position ({position.x_id}, {position.y_id})")
        x_coord, y_coord = self.get_coordinates_from_grid(position)
        return CartesianPosition(x_coord, y_coord, old_height)

    def remove_object(self, obj_list: list[Pickable]) -> CartesianPosition:
        """
        Removes a list of objects from their current position on the grid.

        Args:
            obj_list: The list of objects to be removed.

        Returns:
            The 3D Cartesian coordinates of the updated position after removing the objects.
        """
        position = self.find_object(obj_list[0])
        for obj in obj_list:
            self.object_grid[position.y_id][position.x_id].pop()
            self.height_grid[position.y_id][position.x_id] -= obj.height
            logging.info(f"Removed the {obj.name} with id {obj.id} from the grid position ({position.x_id}, {position.y_id})")

        x_coord, y_coord = self.get_coordinates_from_grid(position)
        return CartesianPosition(x_coord, y_coord, self.height_grid[position.y_id][position.x_id])

    def find_object(self, obj: Pickable) -> GridPosition:
        """
        Finds the position of an object on the grid.

        Args:
            obj: The object to be found.

        Returns:
            The position of the object on the grid.
        """
        for y_idx in range(self.y_num_interval):
            for x_idx in range(self.x_num_interval):
                if obj in self.object_grid[y_idx][x_idx]:
                    return GridPosition(x_idx, y_idx)

    def find_stack_position(self, obj: Pickable, position: GridPosition) -> None | float:
        """
        Finds the stack position of an object at a specific grid position.

        Args:
            obj: The object to find the stack position of.
            position: The position on the grid.

        Returns:
            The stack position of the object if it is at the top of the stack, otherwise None.
        """
        if self.object_grid[position.y_id][position.x_id][-1] is obj:
            return self.height_grid[position.y_id][position.x_id]
        else:
            return None

    def get_coordinates_from_grid(self, position: GridPosition) -> Tuple[float, float]:
        """
        Converts a grid position to 2D Cartesian coordinates.

        Args:
            position: The position on the grid.

        Returns:
            Tuple[float, float]: The 2D Cartesian coordinates derived from the grid position.
        """
        return self.xx[position.x_id], self.yy[position.y_id]

    def set_camera_and_stack_position(self, position_camera: GridPosition, position_stack: GridPosition ) :
        """
        Adds a
        Args:

        Returns:

        """
        self.cam = CameraSpot()
        self.stack = StackSpot()
        self.add_object([self.cam], position_camera)
        self.add_object([self.stack], position_stack)

