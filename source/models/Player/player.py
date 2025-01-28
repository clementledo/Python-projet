import random
from concurrent.futures import ThreadPoolExecutor
import time

from models.Units.unit import Unit
from models.Units.villager import Villager

from models.Buildings.building import Building
from models.Buildings.towncenter import TownCenter
from models.Buildings.house import House
from models.Buildings.barrack import Barrack
from models.Buildings.farm import Farm
from models.Buildings.keep import Keep
from models.Buildings.camp import Camp

from models.Resources.resource_type import ResourceType


class Player:
    def __init__(self, player_id, general_strategy="economic"):
        self.player_id = player_id
        self.buildings = []
        self.units = []
        self.population = 0
        self.max_population = 5
        self.resources = {ResourceType.GOLD: 0, ResourceType.WOOD: 0, ResourceType.FOOD: 0}
        self.general_strategy = general_strategy  # Add general strategy attribute

    def add_building(self, building: Building):
        self.buildings.append(building)
        building.player_id = self.player_id
        if isinstance(building, (TownCenter, House)):
            self.max_population = min(self.max_population + 5, 200)

    def remove_building(self, building: Building):
        self.buildings.remove(building)

    def add_unit(self, unit: Unit):
        if self.population < self.max_population:
            self.units.append(unit)
            self.population += 1
            unit.player_id = self.player_id
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
        with ThreadPoolExecutor(max_workers=5) as executor:  # Limit the number of threads
            futures = []
            available_villagers = [unit for unit in self.units if isinstance(unit, Villager)]
            num_villagers = min(len(available_villagers), 10)  # Limit the number of villagers to 5
            selected_villagers = random.sample(available_villagers, num_villagers)
            for villager in selected_villagers:
                resource_type = random.choice([ResourceType.WOOD, ResourceType.GOLD, ResourceType.FOOD])
                futures.append(executor.submit(self._collect_resources, villager, map, resource_type, clock))
            for future in futures:
                try:
                    future.result()
                except Exception as e:
                    print(f"Exception in thread: {e}")

    def _collect_resources(self, villager, map, resource_type, clock):
        try:
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
        except Exception as e:
            print(f"Exception while collecting resources: {e}")

    def send_units_to_attack(self, game, clock):
        enemy_player = random.choice([player for player in game.players if player != self])
        with ThreadPoolExecutor(max_workers=5) as executor:  # Limit the number of threads
            futures = []
            targets = enemy_player.units + enemy_player.buildings * 3  # Give more weight to buildings
            if targets:
                target = random.choice(targets)
            for unit in self.units:
                if isinstance(unit, Unit):
                    futures.append(executor.submit(self._attack_target, unit, game.map, target, enemy_player, clock))
            for future in futures:
                try:
                    future.result()
                except Exception as e:
                    print(f"Exception in thread: {e}")

    def _attack_target(self, unit, map, target, enemy_player, clock):
        try:
            while unit.hp > 0 and target.hp > 0:
                if abs(unit.position[0] - target.position[0]) <= unit.range and abs(unit.position[1] - target.position[1]) <= unit.range:
                    unit.attack_target(target, map, enemy_player)
                    time.sleep(1) 
                else:
                    unit.move_adjacent_to(map, target)
                    while unit.path:
                        unit.update_position()
                        if abs(unit.position[0] - target.position[0]) <= unit.range and abs(unit.position[1] - target.position[1]) <= unit.range:
                            unit.attack_target(target, map, enemy_player)
                            time.sleep(1)  # Add a delay after attacking
                            break
                        clock.tick(60)
        except Exception as e:
            print(f"Exception while attacking: {e}")
        finally:
            if unit.hp <= 0:
                print(f"{unit.name} has died and its thread is stopping.")
            if target.hp <= 0:
                print(f"{target.name} has died and its thread is stopping.")

    def create_villager(self, map):
        town_center = next((b for b in self.buildings if isinstance(b, TownCenter)), None)
        if town_center:
            town_center.spawn_villager(map, self)
        else:
            raise ValueError("No TownCenter available to spawn a Villager")

    # Add a method to build a building

    def build(self, building: Building, map, villagers, clock):
        if not villagers:
            raise ValueError("No villagers available to build")
        nominal_time = building.build_time
        actual_time = 3 * nominal_time / (len(villagers) + 2)
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=len(villagers)) as executor:
            futures = []
            for villager in villagers:
                futures.append(executor.submit(self._move_villager_to_building_site, villager, map, building, clock))
            for future in futures:
                try:
                    future.result()
                except Exception as e:
                    print(f"Exception in thread: {e}")

        while time.time() - start_time < actual_time:
            time.sleep(0.1)  # Simulate building time
        map.add_building(building)
        self.add_building(building)
        for resource, amount in building.cost.items():
            self.resources[resource] -= amount
        print(f"{building.name} built at {building.position}")

    def _move_villager_to_building_site(self, villager, map, building, clock):
        villager.move_adjacent_to_building_site(map, building)
        while villager.path:
            villager.update_position()
            clock.tick(60)

    def send_units_to_build(self, building: Building, map, clock):
        # Find a valid position near existing buildings
        position = self._find_valid_building_position(map, building.size)
        if position:
            building.position = position
            # Select villagers to build
            available_villagers = [unit for unit in self.units if isinstance(unit, Villager)]
            if available_villagers:
                print(f"Sending {len(available_villagers)} villagers to build {building.name}")
                num_villagers = min(len(available_villagers), 5)  # Limit the number of villagers to 5
                selected_villagers = random.sample(available_villagers, num_villagers)
                self.build(building, map, selected_villagers, clock)
            else:
                raise ValueError("No villagers available to build")
        else:
            raise ValueError("No valid position available to build")

    def _find_valid_building_position(self, map, size):
        for building in self.buildings:
            for dx in range(-5, 6):
                for dy in range(-5, 6):
                    x, y = building.position[0] + dx, building.position[1] + dy
                    if 0 <= x < map.width and 0 <= y < map.height:
                        if self._can_place_building(map, x, y, size):
                            return (x, y)
        return None

    def _can_place_building(self, map, x, y, size):
        if x + size[0] > map.width or y + size[1] > map.height:
            return False
        for i in range(size[1]):
            for j in range(size[0]):
                tile = map.get_tile(x + j, y + i)
                if tile.occupant is not None or tile.has_resource():
                    return False
        return True
    
    # Add a method to play a turn

    def play_turn(self, game, clock):
        strategy = self._choose_strategy()
        if strategy == "economic":
            self._economic_strategy(game, clock)
        else:
            self._aggressive_strategy(game, clock)

    def _economic_strategy(self, game, clock):
        if Farm not in [type(building) for building in self.buildings]:
            self.send_units_to_build(Farm(), game.map, clock)
        self.send_villager_to_collect(game.map, clock)
        if self.resources[ResourceType.FOOD] >= 50 and self.population < self.max_population:
            self.create_villager(game.map)
        if self.population + 5 >= self.max_population:
            if TownCenter not in [type(building) for building in self.buildings] and self.resources[ResourceType.WOOD] >= 350:
                self.send_units_to_build(TownCenter(), game.map, clock)
            elif self.resources[ResourceType.WOOD] >= 25:
                self.send_units_to_build(House(), game.map, clock)
        self._defend_buildings(game, clock)

    def _aggressive_strategy(self, game, clock):
        self.send_units_to_attack(game, clock)
        self._defend_buildings(game, clock)
        
    def _choose_strategy(self):
        if self.general_strategy == "economic":
            return random.choices(["economic", "aggressive"], [0.7, 0.3])[0]
        else:
            return random.choices(["economic", "aggressive"], [0.3, 0.7])[0]
        
    # Add a method to defend buildings

    def _defend_buildings(self, game, clock):
        for building in self.buildings:
            if building.hp < building.max_hp:
                self._send_units_to_defend(building, game, clock)

    def _send_units_to_defend(self, building, game, clock):
        with ThreadPoolExecutor(max_workers=5) as executor:  # Limit the number of threads
            futures = []
            for enemy_player in game.players:
                if enemy_player != self:
                    for enemy_unit in enemy_player.units:
                        if abs(enemy_unit.position[0] - building.position[0]) <= building.size[0] and abs(enemy_unit.position[1] - building.position[1]) <= building.size[1]:
                            for unit in self.units:
                                if isinstance(unit, Unit):
                                    futures.append(executor.submit(self._defend_target, unit, game.map, enemy_unit, clock))
            for future in futures:
                try:
                    future.result()
                except Exception as e:
                    print(f"Exception in thread: {e}")

    def _defend_target(self, unit, map, target, clock):
        try:
            while unit.hp > 0 and target.hp > 0:
                if abs(unit.position[0] - target.position[0]) <= unit.range and abs(unit.position[1] - target.position[1]) <= unit.range:
                    unit.attack_target(target, map, self)
                    time.sleep(1)
                else:
                    unit.move_adjacent_to(map, target)
                    while unit.path:
                        unit.update_position()
                        if abs(unit.position[0] - target.position[0]) <= unit.range and abs(unit.position[1] - target.position[1]) <= unit.range:
                            unit.attack_target(target, map, self)
                            time.sleep(1)  # Add a delay after attacking
                            break
                        clock.tick(60)
        except Exception as e:
            print(f"Exception while defending: {e}")
       
    def __repr__(self):
        return (f"Player(id={self.player_id}, buildings={len(self.buildings)}, "
                f"units={len(self.units)}, population={self.population}/{self.max_population}, "
                f"resources={self.resources})")
