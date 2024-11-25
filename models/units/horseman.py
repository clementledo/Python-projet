from models.units.unit import Unit

class Horseman(Unit):
    def __init__(self, x, y, map_instance):
        super().__init__(x, y, unit_type="Horseman", atk=4, speed=1.2, hp=45, map=map_instance)
        self.cost = {"food": 80, "gold": 20}
        self.training_time = 30