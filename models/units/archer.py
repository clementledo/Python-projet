from models.units.unit import Unit

class Archer(Unit):
    def __init__(self, x, y,map):
        super().__init__(x, y, "archer", 2, 0.8, 25, map)