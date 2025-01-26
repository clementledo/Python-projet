from source.models.Buildings.building import Building

class Keep(Building):
    def __init__(self, position=(0, 0)):
        super().__init__(name="Keep", build_time=80, hp=800, size=(1, 1), position=position)