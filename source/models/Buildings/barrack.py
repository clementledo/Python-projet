from source.models.Buildings.building import Building

class Barracks(Building):
    def __init__(self, position=(0, 0)):
        super().__init__(name="Barracks", build_time=50, hp=500, size=(3, 3), position=position)