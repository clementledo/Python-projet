from models.Units.unit import Unit
from models.Buildings.building import Building
from models.Resources.tile import Tile

class Villager(Unit):
    def __init__(self, position=(0, 0)):
        super().__init__(name="Villager", hp=25, attack=2, speed=0.8, position=position)
        self.carry_capacity = 20
        self.resource_collected = 0
        self.collection_rate = 25  # 25 resources per minute

    def build(self, building: Building, num_villagers=1):
        nominal_time = building.build_time
        actual_time = 3 * nominal_time / (num_villagers + 2)
        return actual_time

    def collect_resource(self, tile: Tile):
        if self._is_adjacent(tile) and tile.has_resource():
            amount = min(self.collection_rate // 60, tile.resource.quantity, self.carry_capacity - self.resource_collected)
            self.resource_collected += amount
            tile.resource.quantity -= amount
            if tile.resource.quantity <= 0:
                tile.resource = None

    def drop_resource(self):
        collected = self.resource_collected
        self.resource_collected = 0
        return collected

    def _is_adjacent(self, tile: Tile):
        return abs(self.position[0] - tile.position[0]) <= 1 and abs(self.position[1] - tile.position[1]) <= 1

    def __repr__(self):
        return (f"Villager(name={self.name}, hp={self.hp}, attack={self.attack}, "
                f"speed={self.speed}, position={self.position}, carry_capacity={self.carry_capacity}, "
                f"resource_collected={self.resource_collected}, collection_rate={self.collection_rate})")