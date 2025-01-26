from .building import Building

class Stable(Building):
    def __init__(self, position=(0, 0)):
        super().__init__(name="Stable", build_time=50, hp=500, size=(3, 3), position=position, symbol="S")