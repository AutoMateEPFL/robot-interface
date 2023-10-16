import itertools

#TODO: needs to be renamed as not all inheriting classes can be picked up
class Pickable:
    """
    This class defines a general object which the robot can pickup
    """

    # ensures that each object has unique ID
    id_iter = itertools.count()


    def __init__(self) -> None:
        self.id = next(self.id_iter)

class PlateHolder(Pickable):
    """
    This class represents a plate holder with a certain floor thickness
    """
    height = 5
    name = "Plate Holder"
    def __init__(self,experiment):
        super().__init__()
        self.experiment = experiment

class SmallPetriBottom(Pickable):
    """
    This class defines the bottom part of a petri dish
    """
    name = "Small Petri Bottom"
    height = 12.5
    def __init__(self):
        super().__init__()

class SmallPetriTop(Pickable):
    """
    This class defines the top part of a small petri dish
    """
    height = 8.5
    name = "Small Petri Top"
    def __init__(self):
        super().__init__()
