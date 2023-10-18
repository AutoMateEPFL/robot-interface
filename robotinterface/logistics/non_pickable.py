import itertools

#TODO: needs to be renamed as not all inheriting classes can be picked up
class NonPickable:
    """
    This class defines a general object which the robot cannot pickup
    """

    # ensures that each object has unique ID
    id_iter = itertools.count()

    def __init__(self) -> None:
        self.id = next(self.id_iter)

class CameraSpot(NonPickable):
    """
    This class represents a plate holder with a certain floor thickness
    """
    height = 0
    name = "Camera"
    def __init__(self):
        super().__init__()

class StackSpot(NonPickable):
    """
    This class defines the bottom part of a petri dish
    """
    name = "Stack"
    height = 0
    def __init__(self):
        super().__init__()

