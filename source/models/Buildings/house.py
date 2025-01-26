from .building import Building

class House(Building):
    def __init__(self, position=(0, 0)):
        super().__init__(name="House", build_time=25, hp=200, size=(2, 2), position=position, symbol="H")