from .building import Building
from models.Resources.resource_type import ResourceType

class Stable(Building):
    def __init__(self, position=(0, 0)):
        super().__init__(name="Stable", build_time=50, hp=500, size=(3, 3), position=position, symbol="S")
        self.offset_x = 75
        self.offset_y = 25
        self.cost = {ResourceType.WOOD: 175}