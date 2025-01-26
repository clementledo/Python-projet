from .building import Building

class TownCenter(Building):
    def __init__(self, position=(0, 0)):
        super().__init__(name="Town Centre", build_time=150, hp=1000, size=(4, 4), position=position, symbol="T")