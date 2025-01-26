from models.Units.unit import Unit
from models.Buildings.building import Building
from models.Buildings.towncenter import TownCenter
from models.Buildings.camp import Camp
from models.Buildings.farm import Farm
from models.Resources.tile import Tile
from models.Resources.resource import Resource
import math

class Villager(Unit):
    def __init__(self, position=(0, 0)):
        super().__init__(name="Villager", hp=25, attack=2, speed=0.8, position=position, symbol="v")
        self.carry_capacity = 20
        self.resource_collected = 0
        self.collection_rate = 25 #/ 60  # 25 resources per minute

    def build(self, building: Building, num_villagers=1):
        nominal_time = building.build_time
        actual_time = 3 * nominal_time / (num_villagers + 2)
        return actual_time

    def collect_resource(self, tile: Tile, map):
        if self._is_adjacent(tile) and tile.has_resource():
            amount = min(self.collection_rate, tile.resource.quantity, self.carry_capacity - self.resource_collected)
            self.resource_collected += amount
            if isinstance(tile.occupant, Farm):
                farm = tile.occupant
                for i in range(farm.size[1]):
                    for j in range(farm.size[0]):
                        farm_tile = map.get_tile(farm.position[0] + j, farm.position[1] + i)
                        if farm_tile.has_resource():
                            farm_tile.resource.quantity -= amount
                            if farm_tile.resource.quantity <= 0:
                                farm_tile.resource = None
                if all(map.get_tile(farm.position[0] + j, farm.position[1] + i).resource is None for i in range(farm.size[1]) for j in range(farm.size[0])):
                    map.remove_building(farm)
            else:
                tile.resource.quantity -= amount
                if tile.resource.quantity <= 0:
                    tile.resource = None

    def drop_resource(self, map):
        if self._is_adjacent_to_drop_point(map):
            collected = self.resource_collected
            self.resource_collected = 0
            return collected
        else:
            raise ValueError("Villager is not adjacent to a TownCentre or Camp")

    def _is_adjacent(self, tile: Tile):
        return abs(self.position[0] - tile.position[0]) <= 1 and abs(self.position[1] - tile.position[1]) <= 1

    def _is_adjacent_to_drop_point(self, map):
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                x, y = self.position[0] + dx, self.position[1] + dy
                if 0 <= x < map.width and 0 <= y < map.height:
                    tile = map.get_tile(x, y)
                    if isinstance(tile.occupant, (TownCenter, Camp)):
                        return True
        return False

    def find_nearest_resource(self, map):
        min_distance = float('inf')
        nearest_resource = None
        for y in range(map.height):
            for x in range(map.width):
                tile = map.get_tile(x, y)
                if tile.has_resource():
                    distance = math.sqrt((self.position[0] - x) ** 2 + (self.position[1] - y) ** 2)
                    if distance < min_distance:
                        min_distance = distance
                        nearest_resource = tile
        return nearest_resource

    def __repr__(self):
        return (f"Villager(name={self.name}, hp={self.hp}, attack={self.attack}, "
                f"speed={self.speed}, position={self.position}, carry_capacity={self.carry_capacity}, "
                f"resource_collected={self.resource_collected}, collection_rate={self.collection_rate})")