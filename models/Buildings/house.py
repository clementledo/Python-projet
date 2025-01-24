from models.Buildings.building import Building

class House(Building) :
    def __init__(self, pos) :
        super().__init__(self, 25, 200, (2,2), 'H', pos)
        self.cost["wood"] = 25