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

class PlateHolder(NonPickable):
    """
    This class represents a plate holder with a certain floor thickness
    """
    height = 5
    name = "Plate Holder"
    def __init__(self,experiment_list=[],associated_name="",num_experiments=0):
        super().__init__()
        self.experiment_list = experiment_list
        self.associated_name = associated_name
        self.num_experiments = num_experiments

    def set_associated_name(self,associated_name):
        self.associated_name = associated_name

class CameraSpot(NonPickable):
    """
    This class represents a camera spot
    """
    height = -1.0 # Possible offset to adjust for the grip thickness
    name = "Camera"
    def __init__(self,grid_position):
        super().__init__()
        self._grid_position = grid_position

class StackSpot(NonPickable):
    """
    This class defines a stack spot
    """
    name = "Stack"
    height = 0
    def __init__(self,grid_position):
        super().__init__()
        self._grid_position = grid_position

