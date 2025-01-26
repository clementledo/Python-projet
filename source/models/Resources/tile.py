from .resource import Resource
from .terrain_type import Terrain_type

class Tile:
    def __init__(self, x, y, terrain_type = Terrain_type.GRASS, occupant=None, resource: Resource = None):
        self.x = x
        self.y = y
        self.terrain_type = terrain_type
        self.occupant = occupant
        self.resource = resource

    def __repr__(self):
        return f"Tile(x={self.x}, y={self.y}, occupant={self.occupant}, resource={self.resource})"

    def is_occupied(self):
        return self.occupant is not None

    def has_resource(self):
        return self.resource is not None