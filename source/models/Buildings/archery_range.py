from models.Buildings.building import Building
from models.Resources.resource_type import ResourceType

class ArcheryRange(Building):
    def __init__(self, position=(0, 0)):
        super().__init__(name="Archery Range", build_time=50, hp=500, size=(3, 3), position=position, symbol="A")
        self.offset_x = 100
        self.offset_y = 100
        self.cost = {ResourceType.WOOD: 175}
