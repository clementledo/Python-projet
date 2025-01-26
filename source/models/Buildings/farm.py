from models.Buildings.building import Building

class Farm(Building):
    def __init__(self, position=(0, 0)):
        super().__init__(name="Farm", build_time=10, hp=100, size=(2, 2), position=position, walkable=True, symbol="F")