import itertools

#TODO: needs to be renamed as not all inheriting classes can be picked up
class NonPickable:
    """
    This class defines a general object which the robot cannot pickup
    """

    # ensures that each object has unique ID
    id_iter = itertools.count()

    def __init__(self,grid_position) -> None:
        self.id = next(self.id_iter)
        self._grid_position = grid_position

class CameraSpot(NonPickable):
    """
    This class represents a plate holder with a certain floor thickness
    """
    height = -1.0 # Possible offset to adjust for the grip thickness
    name = "Camera"
    def __init__(self,grid_position):
        super().__init__(grid_position)

class StackSpot(NonPickable):
    """
    This class defines the bottom part of a petri dish
    """
    name = "Stack"
    height = 0
    def __init__(self,grid_position):
        super().__init__(grid_position)

