from building.building import Building
from resource.tile import Type

class Farm(Building):
    def __init__(self, x, y, owner, map):
        cost = {"Food": 0, "Wood": 100, "Gold": 0}
        super().__init__(x, y, Type.Farm, health=500, cost=cost, owner=owner, map=map, size=(2, 2))