from models.Resources.tile import Tile
from models.Resources.resource import Resource, ResourceType
from models.Buildings.building import Building
from models.Buildings.farm import Farm
from models.Units.unit import Unit
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

    def add_building(self, building: Building):
        if not self._can_place_building(building):
            raise ValueError("Cannot place building at the specified location")
        for i in range(building.size[1]):
            for j in range(building.size[0]):
                self.grid[building.position[1] + i][building.position[0] + j].occupant = building
                if isinstance(building, Farm):
                    self.grid[building.position[1] + i][building.position[0] + j].resource = Resource(ResourceType.FOOD, 300)

    def remove_building(self, building: Building):
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x].occupant == building:
                    self.grid[y][x].occupant = None

    def _can_place_building(self, building: Building):
        if building.position[0] + building.size[0] > self.width or building.position[1] + building.size[1] > self.height:
            return False
        for i in range(building.size[1]):
            for j in range(building.size[0]):
                if self.grid[building.position[1] + i][building.position[0] + j].occupant is not None or self.grid[building.position[1] + i][building.position[0] + j].has_resource():
                    return False
        return True

    def add_unit(self, unit: Unit):
        x, y = unit.position
        if 0 <= x < self.width and 0 <= y < self.height:
            if self.grid[y][x].occupant is None:
                self.grid[y][x].occupant = unit
            else:
                raise ValueError("Tile is already occupied")
        else:
            raise ValueError("Coordinates out of bounds")

    def remove_unit(self, unit: Unit):
        x, y = unit.position
        if 0 <= x < self.width and 0 <= y < self.height:
            if self.grid[y][x].occupant == unit:
                self.grid[y][x].occupant = None
            else:
                raise ValueError("Unit not found at the specified location")
        else:
            raise ValueError("Coordinates out of bounds")

    def update(self):
        for y in range(self.height):
            for x in range(self.width):
                tile = self.grid[y][x]
                if isinstance(tile.occupant, Unit):
                    unit = tile.occupant
                    if unit.position != (x, y):
                        self.grid[y][x].occupant = None
                        new_x, new_y = unit.position
                        self.grid[new_y][new_x].occupant = unit

    def display(self):
        for y in range(self.height):
            for x in range(self.width):
                tile = self.grid[y][x]
                if tile.occupant:
                    print(tile.occupant.symbol, end=' ')
                elif tile.has_resource():
                    print(tile.resource.type.value, end=' ')
                else:
                    print('.', end=' ')
            print()

    # @staticmethod
    # def generate_random_map(width, height, map_type="default"):
    #     map_instance = Map(width, height)
    #     if map_type == "default":
    #         Map._generate_default_map(map_instance)
    #     elif map_type == "central_gold":
    #         Map._generate_central_gold_map(map_instance)
    #     else:
    #         raise ValueError("Unknown map type")
    #     return map_instance

    # @staticmethod
    # def _generate_default_map(map_instance):
    #     for y in range(map_instance.height):
    #         for x in range(map_instance.width):
    #             if random.random() < 0.1:  # 10% chance to place a resource
    #                 resource_type = random.choice([ResourceType.WOOD, ResourceType.GOLD])
    #                 if resource_type == "gold":
    #                     map_instance.grid[y][x].resource = Resource(resource_type, 800)
    #                 else:
    #                     map_instance.grid[y][x].resource = Resource(resource_type, 100)

    # @staticmethod
    # def _generate_central_gold_map(map_instance):
    #     center_x, center_y = map_instance.width // 2, map_instance.height // 2
    #     radius_x = int(map_instance.width * 0.2)
    #     radius_y = int(map_instance.height * 0.2)
    #     for y in range(map_instance.height):
    #         for x in range(map_instance.width):
    #             if abs(x - center_x) < radius_x and abs(y - center_y) < radius_y:
    #                 if random.random() < 0.3:  # 30% chance to place gold
    #                     map_instance.grid[y][x].resource = Resource(ResourceType.GOLD, 800)
    #             elif random.random() < 0.1:  # 10% chance to place other resources
    #                 map_instance.grid[y][x].resource = Resource(ResourceType.WOOD, 100)

    def add_resources(self, map_type="default"):
        if map_type == "default":
            self._generate_default_resources()
        elif map_type == "central_gold":
            self._generate_central_gold_resources()
        else:
            raise ValueError("Unknown map type")

    def _generate_default_resources(self):
        for y in range(self.height):
            for x in range(self.width):
                if random.random() < 0.1:  # 10% chance to place a resource
                    if self.grid[y][x].occupant is None:
                        resource_type = random.choice([ResourceType.WOOD, ResourceType.GOLD])
                        if resource_type == ResourceType.GOLD:
                            self.grid[y][x].resource = Resource(resource_type, 800)
                        else:
                            self.grid[y][x].resource = Resource(resource_type, 100)

    def _generate_central_gold_resources(self):
        center_x, center_y = self.width // 2, self.height // 2
        radius_x = int(self.width * 0.2)
        radius_y = int(self.height * 0.2)
        for y in range(self.height):
            for x in range(self.width):
                if abs(x - center_x) < radius_x and abs(y - center_y) < radius_y:
                    if random.random() < 0.3:  # 30% chance to place gold
                        if self.grid[y][x].occupant is None:
                            self.grid[y][x].resource = Resource(ResourceType.GOLD, 800)
                elif random.random() < 0.1:  # 10% chance to place other resources
                    if self.grid[y][x].occupant is None:
                        self.grid[y][x].resource = Resource(ResourceType.WOOD, 100)
