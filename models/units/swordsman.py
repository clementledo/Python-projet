
from .unit import Unit

class Swordsman(Unit):
    def __init__(self, x, y, map_instance):
        super().__init__(x, y, unit_type="Swordsman", atk=4, speed=0.9, hp=40, map=map_instance)
        self.cost = {"food": 50, "gold": 20}
        self.training_time = 20  # Temps d'entraînement en secondes
        