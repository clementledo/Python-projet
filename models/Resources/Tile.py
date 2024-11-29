from typing import Optional, Union
#from Terrain_type import Terrain_Type
from models.Resources.Terrain_type import Terrain_type

from ..units.unit import Unit
from ..Buildings.building import Building


class Tile:
    def __init__(self, x: int, y: int, terrain_type: Terrain_type, occupant: Optional[Union["Unit", "Building"]] = None):
        self.x = x
        self.y = y
        self.tile_type = terrain_type
        self.terrain_type = terrain_type
        self.occupant = occupant

      

    def __repr__(self):
        return f"Tile(x={self.x}, y={self.y}, terrain_type={self.terrain_type}, occupant={self.occupant})"
