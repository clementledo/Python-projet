from models.Buildings.building import Building
from models.Units.unit import Unit
from models.Buildings.towncenter import TownCenter
from models.Units.villager import Villager
from models.Resources.resource_type import ResourceType
from models.Buildings.house import House
import math
import random
from models.Buildings.farm import Farm
import threading

class Player:
    def __init__(self, player_id, general_strategy="balanced"):
        self.player_id = player_id
        self.buildings = []
        self.units = []
        self.population = 0
        self.max_population = 5
        self.resources = {ResourceType.GOLD: 0, ResourceType.WOOD: 0, ResourceType.FOOD: 0}
        self.general_strategy = general_strategy  # Add general strategy attribute

    def add_building(self, building: Building):
        self.buildings.append(building)
        if isinstance(building, (TownCenter, House)):
            self.max_population = min(self.max_population + 5, 200)

    def remove_building(self, building: Building):
        self.buildings.remove(building)

    def add_unit(self, unit: Unit):
        if self.population < self.max_population:
            self.units.append(unit)
            self.population += 1
        else:
            raise ValueError("Maximum population reached")

    def remove_unit(self, unit: Unit):
        self.units.remove(unit)
        self.population -= 1

    def add_resource(self, resource_type, amount):
        if resource_type in self.resources:
            self.resources[resource_type] += amount
        else:
            raise ValueError("Invalid resource type")

    def send_villager_to_collect(self, map, clock):
        threads = []
        for unit in self.units:
            if isinstance(unit, Villager):
                villager = unit
                resource_type = random.choice([ResourceType.WOOD, ResourceType.GOLD])
                thread = threading.Thread(target=self._collect_resources, args=(villager, map, resource_type, clock))
                threads.append(thread)
                thread.start()
        for thread in threads:
            thread.join()

    def _collect_resources(self, villager, map, resource_type, clock):
        villager.move_adjacent_to_resource(map, resource_type)
        while villager.path:
            villager.update_position()
            clock.tick(60)
        villager.collect_resource()
        villager.move_to_drop_resource(map)
        while villager.path:
            villager.update_position()
            clock.tick(60)
        villager.drop_resource(map, self)

    def play_turn(self, map, enemy_players):
        strategy = self._choose_strategy()
        if strategy == "economic":
            self._economic_strategy(map)
        elif strategy == "aggressive":
            self._aggressive_strategy(map, enemy_players)
        else:
            self._balanced_strategy(map, enemy_players)

    def _choose_strategy(self):
        if self.general_strategy == "economic":
            return random.choices(["economic", "aggressive", "balanced"], [0.6, 0.2, 0.2])[0]
        elif self.general_strategy == "aggressive":
            return random.choices(["economic", "aggressive", "balanced"], [0.2, 0.6, 0.2])[0]
        else:
            return random.choices(["economic", "aggressive", "balanced"], [0.3, 0.3, 0.4])[0]

    def __repr__(self):
        return (f"Player(id={self.player_id}, buildings={len(self.buildings)}, "
                f"units={len(self.units)}, population={self.population}/{self.max_population}, "
                f"resources={self.resources})")
