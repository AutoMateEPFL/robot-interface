import itertools


class Pickable:
    id_iter = itertools.count()

    def __init__(self) -> None:
        self.id = next(self.id_iter)

class PlateHolder(Pickable):
    height = 5
    def __init__(self):
        super().__init__()

class SmallPetriBottom(Pickable):
    height = 7.5
    def __init__(self):
        super().__init__()

class SmallPetriTop(Pickable):
    height = 8.5
    def __init__(self):
        super().__init__()