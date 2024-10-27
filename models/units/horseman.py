from models.units.unit import Unit

class Horseman(Unit):
    def __init__(self, x, y,map):
        super().__init__(x, y, "horseman", 2, 0.8, 25, map)