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
        super().__init__(name="Villager", hp=25, attack=2, speed=0.8, position=position, symbol="v", animation_speed=4, offset_x=50, offset_y=20)
        self.carry_capacity = 20
        self.resource_collected = 0
        self.collection_rate = 25 # 25 resources per minute

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
        self.resource_tile_to_collect = resource_tile
        self.move_adjacent_to(map, resource_tile)
        
    def move_to_drop_resource(self, map):
        tile = self.find_nearest_town_center_camp(map)
        self.move_adjacent_to(map, tile)

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

    def find_nearest_town_center_camp(self, map):
        min_distance = float('inf')
        nearest_building = None
        for y in range(map.height):
            for x in range(map.width):
                tile = map.get_tile(x, y)
                if isinstance(tile.occupant, (TownCenter, Camp)):
                    distance = math.sqrt((self.position[0] - x) ** 2 + (self.position[1] - y) ** 2)
                    if distance < min_distance:
                        min_distance = distance
                        nearest_building = tile.occupant
        return nearest_building

    def collect_resource(self):
        if self._is_adjacent_to_tile(self.resource_tile_to_collect) and self.resource_tile_to_collect.has_resource():
            amount = min(self.collection_rate, self.resource_tile_to_collect.resource.quantity, self.carry_capacity - self.resource_collected)
            self.resource_collected += amount
            self.resource_collected_type = self.resource_tile_to_collect.resource.type
            self.resource_tile_to_collect.resource.quantity -= amount
            if self.resource_tile_to_collect.resource.quantity <= 0:
                self.resource_tile_to_collect.resource = None
            print(f"{self} collected {amount} from {self.resource_tile_to_collect}")
            self.resource_tile_to_collect = None
        else:
            raise ValueError("Villager is not adjacent to the resource tile or resource tile is empty")

    def drop_resource(self, map, player):
        adjacent_tiles = [(self.position[0] + dx, self.position[1] + dy) for dx in [-1, 0, 1] for dy in [-1, 0, 1] if dx != 0 or dy != 0]
        for x, y in adjacent_tiles:
            if 0 <= x < map.width and 0 <= y < map.height:
                tile = map.get_tile(x, y)
                if isinstance(tile.occupant, (TownCenter, Camp)):
                    collected = self.resource_collected
                    player.add_resource(self.resource_collected_type, collected)
                    self.resource_collected = 0
                    print(f"{self} dropped {collected} resources at {tile}")
                    return collected
        raise ValueError("Villager is not adjacent to a TownCenter or Camp")

    def _is_adjacent_to_tile(self, tile: Tile):
        return abs(self.position[0] - tile.position[0]) <= 1 and abs(self.position[1] - tile.position[1]) <= 1

    def __repr__(self):
        return (f"Villager(name={self.name}, hp={self.hp}, attack={self.attack}, "
                f"speed={self.speed}, position={self.position}, carry_capacity={self.carry_capacity}, "
                f"resource_collected={self.resource_collected}, collection_rate={self.collection_rate})")