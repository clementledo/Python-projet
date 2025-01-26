from models.Buildings.building import Building
from models.Units.unit import Unit
from models.Buildings.towncenter import TownCenter
from models.Units.villager import Villager
from models.Resources.resource_type import ResourceType
from models.Buildings.house import House
import math
import random

class Player:
    def __init__(self, player_id):
        self.player_id = player_id
        self.buildings = []
        self.units = []
        self.population = 0
        self.max_population = 5
        self.resources = {ResourceType.GOLD: 0, ResourceType.WOOD: 0, ResourceType.FOOD: 0}

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

    def send_villagers_to_collect(self, resource_type, map, num_villagers=1):
        villagers = [unit for unit in self.units if isinstance(unit, Villager)]
        if len(villagers) < num_villagers:
            raise ValueError("Not enough villagers available")

        for villager in villagers[:num_villagers]:
            nearest_resource = villager.find_nearest_resource(map)
            if nearest_resource and nearest_resource.resource.type == resource_type:
                try:
                    villager.collect_resource(nearest_resource, map)
                except ValueError:
                    villager.move(map, nearest_resource.position)
                    villager.collect_resource(nearest_resource, map)
                drop_point = self._find_nearest_towncenter(villager.position)
                if drop_point:
                    villager.move(map, drop_point.position)
                    collected_amount = villager.drop_resource(map)
                    self.resources[resource_type] += collected_amount
                else:
                    raise ValueError("No TownCenter available for dropping resources")

    def _find_nearest_towncenter(self, position):
        min_distance = float('inf')
        nearest_towncenter = None
        for building in self.buildings:
            if isinstance(building, TownCenter):
                distance = math.sqrt((position[0] - building.position[0]) ** 2 + (position[1] - building.position[1]) ** 2)
                if distance < min_distance:
                    min_distance = distance
                    nearest_towncenter = building
        return nearest_towncenter

    def attack_enemy(self, target, map, enemy_player):
        attacking_units = [unit for unit in self.units if unit.hp > 0]
        if not attacking_units:
            raise ValueError("No units available to attack")

        for unit in attacking_units:
            print(f"Unit {unit} is attacking {target}")
            try:
                unit.attack_target(target, map, enemy_player)
            except ValueError:
                unit.move_to(map, target)
                unit.attack_target(target, map, enemy_player)

    def find_nearest_enemy(self, map, enemy_player):
        min_distance = float('inf')
        nearest_enemy = None
        for unit in enemy_player.units:
            distance = math.sqrt((self.units[0].position[0] - unit.position[0]) ** 2 + (self.units[0].position[1] - unit.position[1]) ** 2)
            if distance < min_distance:
                min_distance = distance
                nearest_enemy = unit
        for building in enemy_player.buildings:
            distance = math.sqrt((self.units[0].position[0] - building.position[0]) ** 2 + (self.units[0].position[1] - building.position[1]) ** 2)
            if distance < min_distance:
                min_distance = distance
                nearest_enemy = building
        return nearest_enemy

    def play_turn(self, map, enemy_players):
        # Example AI behavior for a turn
        if self.resources[ResourceType.WOOD] >= 350 and self.population + 5 >= self.max_population:
            # Try to build a new TownCenter
            position = self._find_valid_building_position(map, TownCenter)
            if position:
                villager = self._get_available_villager()
                if villager:
                    towncenter = TownCenter(position)
                    villager.build(towncenter, map, self)
                    self.add_building(towncenter)
        else:
            # Randomly decide whether to collect resources or attack an enemy
            if random.choice([True, False]):
                self.send_villagers_to_collect(ResourceType.WOOD, map, num_villagers=1)
            else:
                if enemy_players:
                    enemy_player = random.choice(enemy_players)
                    nearest_enemy = self.find_nearest_enemy(map, enemy_player)
                    if nearest_enemy:
                        self.attack_enemy(nearest_enemy, map, enemy_player)

    def _find_valid_building_position(self, map, building_class):
        for y in range(map.height):
            for x in range(map.width):
                building = building_class(position=(x, y))
                if map._can_place_building(building):
                    return (x, y)
        return None

    def _get_available_villager(self):
        for unit in self.units:
            if isinstance(unit, Villager):
                return unit
        return None

    def __repr__(self):
        return (f"Player(id={self.player_id}, buildings={len(self.buildings)}, "
                f"units={len(self.units)}, population={self.population}/{self.max_population}, "
                f"resources={self.resources})")
