class GridPosition:
    """This class defines a 2D position on the fixed grid of the robot

    Attributes:
        x_id The x index on the grid
        y_id The y index on the grid
    """

    def __init__(self, x_id: int, y_id: int) -> None:
        """ Initializes a new instance of the GridPosition class

        Attributes:
            x_id: The x index on the grid
            y_id: The y index on the grid
        """
        self.x_id = x_id
        self.y_id = y_id

    def __eq__(self, other):
        if not isinstance(other, GridPosition):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.x_id == other.x_id and self.y_id == other.y_id


class CartesianPosition:
    """This class defines a 2D position on the fixed grid of the robot

    Attributes:
        x: The x position in cartesian coordinates
        y: The y position in cartesian coordinates
        z: The z position in cartesian coordinates
    """
    
    def __init__(self, x: float, y: float, z: float):
        """ Initializes a new instance of the GridPosition class

        Attributes:
                x: The x position in cartesian coordinates
                y: The y position in cartesian coordinates
                z: The z position in cartesian coordinates
        """    
        self.x = x
        self.y = y
        self.z = z

    def __eq__(self, other):
        if not isinstance(other, CartesianPosition):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.x == other.x and self.y == other.y and self.z == self.z
