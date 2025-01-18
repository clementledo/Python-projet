from .building import Building
from unit.villager import Villager
from resource.tile import Type

class TownHall(Building):
    def __init__(self, x, y, owner, map):
        cost = {"Food": 0, "Wood": 350, "Gold": 0}  # The cost to build a TownHall
        super().__init__(x, y, Type.Town_Hall, health=1000, cost=cost, owner=owner, map= map, size=(4, 4))
        self.villager_count = 0  # Number of villagers spawned by the TownHall
        self.resource_drop_point = True  # The TownHall acts as a resource drop point

    def spawn_villager(self):
        """
        Spawns a villager at the TownHall.
        
        :return: A new villager unit spawned at the TownHall.
        """
        if not self.is_under_construction:
            self.villager_count += 1
            print(f"Villager {self.villager_count} spawned at the TownHall!")
            return Villager(self.x, self.y,self.map)  # Spawn a new unit (villager)
        else:
            print(f"{self} is under construction")
            
    def drop_resources(self, resources):
        """
        Drop resources at the TownHall.
        
        :param resources: A dictionary of resources (Food, Wood, Gold) being dropped.
        """
        if not self.is_under_construction:
            print(f"Dropping resources at the TownHall: {resources}")
        # Logic for adding the dropped resources to the player's or AI's total


