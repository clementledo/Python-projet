from typing import Optional, Union
from terrain_type import TerrainType


class Tile:
    def __init__(self, x: int, y: int, terrain_type: TerrainType, occupant: Optional[Union["Unit", "Building"]] = None):
        self.x = x
        self.y = y
        self.terrain_type = terrain_type
        self.occupant = occupant

    def __repr__(self):
        return f"Tile(x={self.x}, y={self.y}, terrain_type={self.terrain_type}, occupant={self.occupant})"
