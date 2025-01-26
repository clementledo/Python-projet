from models.Buildings.building import Building
from models.Units.unit import Unit
from models.Buildings.towncenter import TownCenter
from models.Units.villager import Villager
from models.Resources.resource_type import ResourceType
from models.Buildings.house import House
import math
import random
from models.Buildings.farm import Farm

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

    def send_villagers_to_collect(self, resource_type, map, num_villagers=1):
        if not self.units:
            return
        villagers = [unit for unit in self.units if isinstance(unit, Villager)]
        if len(villagers) < num_villagers:
            raise ValueError("Not enough villagers available")

        for villager in villagers[:num_villagers]:
            nearest_resource = villager.find_nearest_resource(map, resource_type)
            if nearest_resource and nearest_resource.resource.type == resource_type:
                try:
                    villager.collect_resource(nearest_resource, map)
                    print(f"{villager} collected {villager.resource_collected} {resource_type}")
                except ValueError:
                    villager.move_adjacent_to_resource(map, nearest_resource)
                    villager.collect_resource(nearest_resource, map)
                    print(f"{villager} collected {villager.resource_collected} {resource_type}")
                drop_point = self._find_nearest_towncenter(villager.position)
                if drop_point:
                    villager.move(map, drop_point.position)
                    collected_amount = villager.drop_resource(map)
                    self.resources[resource_type] += collected_amount
                    print(f"{villager} dropped {collected_amount} {resource_type} at {drop_point}")
                else:
                    raise ValueError("No TownCenter available for dropping resources")
            else:
                raise ValueError(f"No {resource_type} resource found for {villager}")

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
        if not self.units:
            return
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
        if not self.units:
            return
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

    def _economic_strategy(self, map):
        villagers = [unit for unit in self.units if isinstance(unit, Villager)]
        if not villagers and self.resources[ResourceType.FOOD] >= 50:
            # Spawn a villager if resources are available, population limit is not reached, and random chance is met
            if self.resources[ResourceType.FOOD] >= 50 and self.population < self.max_population:
                if random.random() < 0.25:  # 25% chance to spawn a villager
                    towncenters = [building for building in self.buildings if isinstance(building, TownCenter)]
                    if towncenters:
                        towncenter = random.choice(towncenters)
                        try:
                            towncenter.spawn_villager(map, self)
                        except ValueError as e:
                            print(e)
            return

        # Prioritize resource collection to avoid running out of any resource
        resource_priority = sorted(self.resources.items(), key=lambda item: item[1])
        resource_types = [resource for resource, _ in resource_priority]

        # Divide tasks among villagers
        num_villagers = len(villagers)
        num_collectors = max(1, num_villagers // 2)
        num_builders = max(1, (num_villagers - num_collectors) // 2)
        num_spawners = num_villagers - num_collectors - num_builders

        # Collect resources, prioritizing the resource with the lowest quantity
        for i in range(num_collectors):
            resource_type = resource_types[i % len(resource_types)]
            try:
                self.send_villagers_to_collect(resource_type, map, num_villagers=1)
            except ValueError as e:
                if resource_type == ResourceType.FOOD:
                    # Build a farm if no food resource is found
                    if self.resources[ResourceType.WOOD] >= 60 and num_builders > 0:
                        existing_farm = any(isinstance(building, Farm) for building in self.buildings)
                        if not existing_farm:
                            position = self._find_valid_building_position(map, Farm)
                            if position:
                                villager = villagers[num_collectors]
                                farm = Farm(position)
                                villager.build(farm, map, self)
                                self.add_building(farm)

        # Spawn a villager if resources are available, population limit is not reached, and random chance is met
        if self.resources[ResourceType.FOOD] >= 50 and self.population < self.max_population and num_spawners > 0:
            if random.random() < 0.25:  # 25% chance to spawn a villager
                towncenters = [building for building in self.buildings if isinstance(building, TownCenter)]
                if towncenters:
                    towncenter = random.choice(towncenters)
                    try:
                        towncenter.spawn_villager(map, self)
                    except ValueError as e:
                        print(e)

    def _aggressive_strategy(self, map, enemy_players):
        # Focus on attacking enemies
        if enemy_players:
            enemy_player = random.choice(enemy_players)
            # Prioritize attacking enemy units
            nearest_enemy_unit = self.find_nearest_enemy_unit(map, enemy_player)
            if nearest_enemy_unit:
                self._attack_or_move_to_target(nearest_enemy_unit, map, enemy_player)
            else:
                # If no enemy units are found, attack enemy buildings
                nearest_enemy_building = self.find_nearest_enemy_building(map, enemy_player)
                if nearest_enemy_building:
                    self._attack_or_move_to_target(nearest_enemy_building, map, enemy_player)

    def _attack_or_move_to_target(self, target, map, enemy_player):
        for unit in self.units:
            if unit.hp > 0:
                if abs(unit.position[0] - target.position[0]) > 1 or abs(unit.position[1] - target.position[1]) > 1:
                    unit.move_to(map, target)
                if abs(unit.position[0] - target.position[0]) <= 1 and abs(unit.position[1] - target.position[1]) <= 1:
                    unit.attack_target(target, map, enemy_player)

    def find_nearest_enemy_unit(self, map, enemy_player):
        if not self.units:
            return
        min_distance = float('inf')
        nearest_enemy = None
        for unit in enemy_player.units:
            distance = math.sqrt((self.units[0].position[0] - unit.position[0]) ** 2 + (self.units[0].position[1] - unit.position[1]) ** 2)
            if distance < min_distance:
                min_distance = distance
                nearest_enemy = unit
        return nearest_enemy

    def find_nearest_enemy_building(self, map, enemy_player):
        if not self.units:
            return
        min_distance = float('inf')
        nearest_enemy = None
        for building in enemy_player.buildings:
            distance = math.sqrt((self.units[0].position[0] - building.position[0]) ** 2 + (self.units[0].position[1] - building.position[1]) ** 2)
            if distance < min_distance:
                min_distance = distance
                nearest_enemy = building
        return nearest_enemy

    def _balanced_strategy(self, map, enemy_players):
        # Example AI behavior for a balanced turn
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
