from .Tile import Tile
from resource import Resource
from .Terrain_type import TerrainType

class ResourceTile(Tile):
    def __init__(self, x: int, y: int, terrain_type: TerrainType, resource: Resource, amount: int, max_amount: int):
        super().__init__(x, y, terrain_type)
        self.resource = resource
        self.amount = amount
        self.max_amount = max_amount
        self.depleted = amount <= 0

    def delete(self):
        self.depleted = True
        self.amount = 0

    def harvest(self, amount: int) -> int:
        if self.depleted:
            return 0
        harvested_amount = min(amount, self.amount)
        self.amount -= harvested_amount
        if self.amount <= 0:
            self.delete()
        return harvested_amount

    def __repr__(self):
        return f"ResourceTile(x={self.x}, y={self.y}, terrain_type={self.terrain_type}, resource={self.resource}, amount={self.amount}, max_amount={self.max_amount}, depleted={self.depleted})"
