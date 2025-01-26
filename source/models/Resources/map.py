from .tile import Tile
from .resource import Resource
from .resource import ResourceType
from models.Buildings.building import Building
import random

class Map:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[Tile((x, y)) for x in range(width)] for y in range(height)]

    def get_tile(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x]
        else:
            raise ValueError("Coordinates out of bounds")

    def set_tile(self, x, y, tile):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x] = tile
        else:
            raise ValueError("Coordinates out of bounds")

    def add_building(self, building: Building, x, y):
        if not self._can_place_building(building, x, y):
            raise ValueError("Cannot place building at the specified location")
        for i in range(building.size[1]):
            for j in range(building.size[0]):
                self.grid[y + i][x + j].occupant = building

    def remove_building(self, building: Building):
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x].occupant == building:
                    self.grid[y][x].occupant = None

    def _can_place_building(self, building: Building, x, y):
        if x + building.size[0] > self.width or y + building.size[1] > self.height:
            return False
        for i in range(building.size[1]):
            for j in range(building.size[0]):
                if self.grid[y + i][x + j].occupant is not None or self.grid[y + i][x + j].has_resource():
                    return False
        return True

    @staticmethod
    def generate_random_map(width, height, map_type="default"):
        map_instance = Map(width, height)
        if map_type == "default":
            Map._generate_default_map(map_instance)
        elif map_type == "central_gold":
            Map._generate_central_gold_map(map_instance)
        else:
            raise ValueError("Unknown map type")
        return map_instance

    @staticmethod
    def _generate_default_map(map_instance):
        for y in range(map_instance.height):
            for x in range(map_instance.width):
                if random.random() < 0.1:  # 10% chance to place a resource
                    resource_type = random.choice([ResourceType.WOOD, ResourceType.GOLD])
                    if resource_type == "gold":
                        map_instance.grid[y][x].resource = Resource(resource_type, 800)
                    else:
                        map_instance.grid[y][x].resource = Resource(resource_type, 100)

    @staticmethod
    def _generate_central_gold_map(map_instance):
        center_x, center_y = map_instance.width // 2, map_instance.height // 2
        for y in range(map_instance.height):
            for x in range(map_instance.width):
                if abs(x - center_x) < 10 and abs(y - center_y) < 10:  # 20x20 central area
                    if random.random() < 0.3:  # 30% chance to place gold
                        map_instance.grid[y][x].resource = Resource(ResourceType.GOLD, 800)
                elif random.random() < 0.1:  # 10% chance to place other resources
                    map_instance.grid[y][x].resource = Resource(ResourceType.WOOD, 100)
