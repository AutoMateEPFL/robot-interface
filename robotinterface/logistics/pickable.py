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
    def __init__(self,experiment,associated_name=""):
        super().__init__()
        self.experiment = experiment
        self.associated_name = associated_name

    def set_associated_name(self,associated_name):
        self.associated_name = associated_name

class SmallPetriBottom(Pickable):
    """
    This class defines the bottom part of a petri dish
    """
    name = "Small Petri Bottom"

    def __init__(self,number="",associated_name="",brand="SARSTEDT"):
        super().__init__()
        self.associated_name = associated_name
        self.number = number
        self.type = brand
        if self.type == "Corning":
            self.height = 12.5
        elif self.type == "SARSTEDT":
            self.height = 5.5

    def set_associated_name(self, associated_name):
        self.associated_name = associated_name

class SmallPetriTop(Pickable):
    """
    This class defines the top part of a small petri dish
    """
    name = "Small Petri Top"

    def __init__(self, number="", associated_name="",brand="SARSTEDT"):
        super().__init__()
        self.associated_name = associated_name
        self.number = number
        self.type = brand
        if self.type == "Corning":
            self.height = 8.5
        elif self.type == "SARSTEDT":
            self.height = 9.5

    def set_associated_name(self, associated_name):
        self.associated_name = associated_name

