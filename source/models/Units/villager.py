from models.Units.unit import Unit
from models.Buildings.building import Building
from models.Buildings.towncenter import TownCenter
from models.Buildings.camp import Camp
from models.Buildings.farm import Farm
from models.Resources.tile import Tile
from models.Resources.resource_type import ResourceType
import math

class Villager(Unit):
    def __init__(self, position=(0, 0)):
        super().__init__(name="Villager", hp=25, attack=2, speed=0.8, position=position, symbol="v", animation_speed=4, offset_x=0, offset_y=20)
        self.carry_capacity = 20
        self.resource_collected = 0
        self.collection_rate = 25 #/ 60  # 25 resources per minute

    def build(self, building: Building, map, player, num_villagers=1):
        if not self._is_adjacent_to_building_site(building):
            self.move_adjacent_to_building_site(map, building)
        
        for resource, amount in building.cost.items():
            if player.resources.get(resource, 0) < amount:
                raise ValueError(f"Not enough {resource} to build {building.name}")

        nominal_time = building.build_time
        actual_time = 3 * nominal_time / (num_villagers + 2)
        if self._can_place_building(building, map):
            for _ in range(int(actual_time)):
                # Simulate building time
                print("building...")
                pass
            map.add_building(building)
            for resource, amount in building.cost.items():
                player.resources[resource] -= amount
        else:
            raise ValueError("Cannot place building at the specified location")

    def move_adjacent_to_building_site(self, map, building: Building):
        self.move_adjacent_to(map, building)

    def move_adjacent_to_resource(self, map, resource_type: ResourceType):
        resource_tile = self.find_nearest_resource_tile(map, resource_type)
        self.move_adjacent_to(map, resource_tile)

    def find_nearest_resource_tile(self, map, resource_type):
        min_distance = float('inf')
        nearest_tile = None
        for y in range(map.height):
            for x in range(map.width):
                tile = map.get_tile(x, y)
                if tile.has_resource() and tile.resource.type == resource_type:
                    distance = math.sqrt((self.position[0] - x) ** 2 + (self.position[1] - y) ** 2)
                    if distance < min_distance:
                        min_distance = distance
                        nearest_tile = tile
        return nearest_tile

    def __repr__(self):
        return (f"Villager(name={self.name}, hp={self.hp}, attack={self.attack}, "
                f"speed={self.speed}, position={self.position}, carry_capacity={self.carry_capacity}, "
                f"resource_collected={self.resource_collected}, collection_rate={self.collection_rate})")