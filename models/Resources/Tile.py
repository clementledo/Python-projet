from typing import Optional, Union
#from Terrain_type import Terrain_Type
from models.Resources.Terrain_type import Terrain_type
from models.Resources.Ressource import Resource

from ..units.unit import Unit
from ..Buildings.building import Building


class Tile:
    def __init__(self, x: int, y: int, terrain_type= Terrain_type.GRASS, occupant: Optional[Union["Unit", "Building"]] = None,starting_resources=None):
        self.x = x
        self.y = y
        self.tile_type = terrain_type
        self.terrain_type = terrain_type
        self.resource=starting_resources
        self.occupant = occupant
    
    def get_type(self):
        return self.tile_type

    
    def serialize(self):
        """Serialize tile data"""
        return {
            "terrain_type": self.terrain_type,  # Changed from terrain_type.name
            "x": self.x,
            "y": self.y,
            "occupant": self.occupant,
            "resource": self.resource.serialize() if hasattr(self, 'resource') and self.resource else None
        }

    @classmethod
    def deserialize(cls, data):
        """Recrée une tuile à partir des données sérialisées."""
        return cls(data['x'], data['y'], data['terrain_type'], data.get('occupant'))


    def __repr__(self):
        return f"Tile(x={self.x}, y={self.y}, terrain_type={self.terrain_type}, occupant={self.occupant})"
