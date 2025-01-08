from .unit import Unit

class Archer(Unit):
    def __init__(self, x, y, map_instance):
        super().__init__(x, y, unit_type="Archer", attack_speed=4, speed=1.0, hp=30, map=map_instance)
        self.cost = {"wood": 25, "gold": 45}
        self.training_time = 35
        self.attack_range = 4   # Portée de l'attaque