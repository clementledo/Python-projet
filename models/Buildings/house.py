from models.Buildings.building import Building

class House(Building) :
    def __init__(self, pos) :
        super().__init__("House", 25, 200, (3,3), 'H', pos)
        self.cost["wood"] = 25