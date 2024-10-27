
from models.units.unit import Unit

class Swordsman(Unit):
    def __init__(self, x, y,map):
        super().__init__(x, y, "swordsman", 2, 0.8, 25, map)