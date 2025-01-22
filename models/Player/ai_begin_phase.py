<<<<<<< HEAD:models/Player/ai.py
# from unit.unit import Unit 
from units.villager import Villager
from Buildings.town_center import Town_center
=======
from units.unit import unitStatus
from building.town_hall import TownHall
>>>>>>> origin/premain:models/Player/ai_begin_phase.py
from resource.tile import Type  


class IA:
    def __init__(self, player_id, game_state):
        self.player_id = player_id
        self.units = []  
        self.game_state = game_state  # Full map data with obstacles and resources
        self.targets = {}  # Store targets for each unit
        self.resources = {"Food": 0, "Wood": 0, "Gold": 0}  
        self.buildings = []
        self.max_unit = 5
        
    def initialize_starting_assets(self, x, y):
        
        self.resources["Food"] = 500
        self.resources["Wood"] = 350
        self.resources["Gold"] = 100
        
        town_hall_position = (x, y)  # You can choose a position on the map
        self.place_building(Town_center, town_hall_position)  # Place Town Hall on the map

        # Spawn 3 villagers near the Town Hall
        for i in range(3):
            villager_position = (town_hall_position[0] + i, town_hall_position[1])
            if self.game_state.is_area_free(villager_position[0], villager_position[1],1,1):
                position = villager_position
            else:
                position = self.find_nearby_available_position(*villager_position, (1, 1))
            
            if position:
                villager = Villager(position[0],position[1],self.game_state)
                self.units.append(villager)
                self.game_state.all_unit.append(villager)
                self.game_state.update_unit_position(villager, None, position)
            else:
                print("No valid position found for villager.")

    def can_afford(self, cost):
        return all(self.resources[res] >= cost[res] for res in cost)

    def deduct_resources(self, cost): 
        for res in cost:
            self.resources[res] -= cost[res]

    def find_nearby_available_position(self, x, y, building_size):
        """Find the nearest available position to build a building."""
        max_radius = max(self.game_state.width, self.game_state.height)  # Limit search within map bounds

        # Spiral outwards from the target location (x, y)
        for radius in range(1, max_radius):
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    new_x, new_y = x + dx, y + dy
                    if self.game_state.is_area_free(new_x, new_y, building_size[0], building_size[1]):
                        return new_x, new_y
                    
        return None  # Return None if no suitable area is found

    def place_building(self, building_type, initial_position):
        """Place a building of the specified type at or near the initial position."""
        x, y = initial_position
        building = building_type(initial_position[0], initial_position[1], "", self.game_state)  # Create the building instance

        # Check if there's enough resources to build it
        if not self.can_afford(building.cost):
            print(f"Not enough resources to build {building_type.__name__}.")
            return

        # First, try to place the building at the initial position
        if self.game_state.is_area_free(x, y, building.size[0], building.size[1]):
            self.game_state.place_building(building)
            self.buildings.append(building)
            self.deduct_resources(building.cost)
            print(f"AI placed {building_type.__name__} at position ({x}, {y}).")
        else:
            # Find the nearest available position
            new_position = self.find_nearby_available_position(x, y, building.size)
            if new_position:
                building.position = new_position
                self.game_state.place_building(building)
                self.buildings.append(building)
                self.deduct_resources(building.cost)
                print(f"AI placed {building_type.__name__} near position ({new_position[0]}, {new_position[1]}).")
            else:
                print("No suitable position found to place the building.")

    def spawn_villager(self, town_hall):
        """Spawn a new villager if the AI can afford it."""
        villager_cost = {'Food': 50}  # Villager costs 50 Food
        if self.can_afford(villager_cost):
            # Deduct resources and spawn a new villager
            self.deduct_resources(villager_cost)
            villager_position = (town_hall.position[0], town_hall.position[1] + 1)
            if self.game_state.is_area_free(villager_position[0], villager_position[1],1,1):
                position = villager_position
            else:
                position = self.find_nearby_available_position(*villager_position, (1, 1))
            
            if position:
                villager = Villager(position[0],position[1],self.game_state)
                self.units.append(villager)
                self.game_state.all_unit.append(villager)
                self.game_state.update_unit_position(villager, None, position)
                print(f"AI has spawned a new villager!")
        else:
            print(f"{self.player_id} cannot afford to spawn a villager.")
    def get_unit_by_status(self, status):
        units_with_status = []
        for unit in self.units:
            if unit.status == status:  # Assuming unit has a 'status' attribute
                units_with_status.append(unit)
        return units_with_status
 
    def change_unit_status(self, unit, new_status):
        if unit in self.units:
          unit.status = new_status  
          print(f"Unit at {unit.position} status changed to {new_status}.")
        else:
           print(f"Unit {unit} not found in AI's unit list.")


    def manage_resources(self):
        """Manage resource gathering by villagers."""
        for unit in self.units:
            if isinstance(unit, Villager):
                unit.collect_resources(self)

    def control_buildings(self):
        """Control the AI's buildings (e.g., TownHall to spawn villagers)."""
        for building in self.buildings:
            if isinstance(building, Town_center):
                # AI decision to spawn a villager
                if len(self.units) < 10 and self.resources["Food"] > 50:  # Example: If AI has fewer than 10 units
                    self.spawn_villager(building)

    def set_target(self, unit, target):
        """
        Set a target for a specific unit.
        """
        self.targets[unit] = target
    
    def find_nearby_villager(self, enemy_villager):
        villagers = [u for u in enemy_villager if u.units_type == "Villager"]
        return villagers[0] if villagers else enemy_villager[0]
    
    def find_nearby_targets(self, unit, enemy_units, range = 20):
        """
        Find a nearby target within the given range for a specific unit.
        
        :param unit: The unit searching for a target.
        :param all_units: A list of all units on the map.
        :param range: The range within which the unit can search for targets.
        :return: The nearest target if found, or None.
        """
        closest_target = None
        min_distance = float('inf')

        for other_unit in enemy_units:
            if other_unit != unit and other_unit not in self.units:  # Avoid targeting itself or friendly units
                distance = self.get_distance(unit.position, other_unit.position)
                if distance <= range and distance < min_distance:
                    min_distance = distance
                    closest_target = other_unit
                    #print(f"{unit.unit_type} target {closest_target.unit_type}")

        return closest_target

    def gather_resource(self, unit):

        x, y = unit.position[0], unit.position[1]
        resource_type = self.game_state[y][x]  # Check the map tile the unit is on
        if resource_type == 'F':
                  self.resources["Food"] += 1 
                  print(f"{unit.unit_type} gathered Food. Total: {self.resources['Food']}")
                  self.game_state[y][x] = ' '  # Clear the resource from the map after gathering
        elif resource_type == 'W':
                  self.resources["Wood"] += 1 
                  print(f"{unit.unit_type} gathered Wood. Total: {self.resources['Wood']}")
                  self.game_state[y][x] = ' '
        elif resource_type == 'G':
                  self.resources["Gold"] += 1 
                  print(f"{unit.unit_type} gathered Gold. Total: {self.resources['Gold']}")
                  self.game_state[y][x] = ' '

    def find_nearby_resources(self, unit, resource_type):
        """
        Find nearby resources (F, W, G) for a specific unit.
        
        :param unit: The unit searching for resources.
        :param resource_type: The type of resource to search for ('F', 'W', 'G').
        :return: The nearest resource position or None.
        """
        closest_resource = None
        min_distance = float('inf')
        
        # Scan the map for nearby resources
        for y, row in enumerate(self.game_state.grid):
            for x, tile in enumerate(row):
                if tile.get_type() == resource_type:
                    distance = self.get_distance(unit.position, (x, y))
                    if distance < min_distance:
                        min_distance = distance
                        closest_resource = (x, y)
        if closest_resource:
            print(f"{unit.unit_type} found {resource_type} at {closest_resource}")
        return closest_resource

    def find_nearby_available_position(self, x, y, building_size):
        max_radius = max(self.game_state.largeur, self.game_state.hauteur)  
        max_radius = max(self.map_data.largeur, self.map_data.hauteur)  
        for radius in range(1, max_radius):
            for dx in range(-radius, radius + 1):
                 for dy in range(-radius, radius + 1):
                    new_x, new_y = x + dx, y + dy 
                    if 0 <= new_x < self.game_state.largeur and 0 <= new_y < self.game_state.hauteur:
                    if 0 <= new_x < self.map_data.largeur and 0 <= new_y < self.map_data.hauteur:
                        if self.is_area_free(new_x, new_y, building_size[0], building_size[1]):
                            return new_x, new_y

        print("No valid position found for building.")
        return None

    """actiontype : Attack dans classe uml"""
    def make_decision(self, all_units):
    
        self.control_buildings()
        
        for unit in self.units:
            # First priority: attack nearby enemies
            if unit in self.targets:
                target = self.targets[unit]
                if self.get_distance(unit.position, target.position) > 1:
                    # Move towards the target if not in range to attack
                    path = self.find_path(unit, target.position)
                    if path:
                        next_step = path[0]
                        unit.move_towards(next_step, self.game_state)
                elif target.health > 0:
                    # Attack the target if within range
                    unit.atk(target)
                if target.health <= 0:
                    del self.targets[unit] 

            else:
                # No target assigned, search for nearby enemies or resources
                target = self.find_nearby_targets(unit, all_units)
                
                if target:
                    self.set_target(unit, target)
                else:
                
                    # No enemy target, search for resources
                    resource_location = self.find_nearby_resources(unit)
                    if resource_location:
                        # Move towards the resource
                        path = self.find_path(unit, resource_location)
                        if path:
                            next_step = path[0]
                            unit.move_towards(next_step, self.game_state)
                        else:
                            # If the unit is already on the resource tile, gather it
                            self.gather_resource(unit)

    def get_distance(self, pos1, pos2):
        #Get the Manhattan distance between two positions.
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def find_path(self, unit, destination):
        #Find the shortest path to the destination using map data.
        return unit.find_path(destination, self.game_state.grid)

    def execute_begin_phase(self):
        # 0. Build Farm
        if self.buildings['Farm'] == 0:
            position = self.find_nearby_available_position()
            if position:
                self.construct_building('Farm', position)
        
        # 1. Train Villagers if possible
        for town_hall in self.buildings['TownHall']:
            if town_hall.is_idle() and self.resources['Food'] >= 50:
                town_hall.spawn_villager()

        # 2. Allocate Villagers to resources
        self.allocate_villagers()

        # 3. Build new Town Halls if conditions are met
        if len(self.buildings['TownHall']) < 4 and self.resources['Wood'] >= 350:
            position = self.find_building_position('TownHall')
            if position:
                self.construct_building('TownHall', position)

        if len(self.units) + 5 < self.max_unit:
            if self.resources['Wood'] >= 25:
                position = self.find_building_position('House')
                if position:
                    self.construct_building('House',position)
            else:
                self.balance_resources()
        # 4. Adjust strategy if resources are unbalanced
        self.balance_resources()
    
    def allocate_villagers(self):
        available_villagers = self.get_available_villagers()
        villager_farm = []
        for _ in range(len(self.buildings['TownHall'])*4):
            if available_villagers:
                villager = available_villagers.pop(0)
                villager_farm.append(villager)
        villager_wood = available_villagers
        
        for villager in villager_farm:
            pos = self.find_nearby_resources(villager,Type.Food)
            if pos:
                if villager.position != pos:
                    path = self.find_path(villager, pos)
                    if path:
                        next_step = path[0]
                        villager.move_towards(next_step, self.game_state)
                else:
                    self.gather_resource(villager, pos, 100) 
                         
        for villager in villager_wood:
            pos = self.find_nearby_resources(villager,Type.Wood)
            if pos:
                if self.get_distance(villager.position, pos) > 1:
                    path = self.find_path(villager, pos)
                    if path:
                        next_step = path[0]
                        villager.move_towards(next_step, self.game_state)
                else:
                    self.gather_resource(villager, pos, 100)
        for building in self.buildings:
            if isinstance(building, Town_center):
                for _ in range(5):
                    for villager in available_villagers:
                        pos = self.find_nearby_resources(villager,Type.Food)
                        if villager.position != pos:
                                villager.move_towards(pos, self.map_data)
                        villager.gather_resources()
                        available_villagers.remove(villager)
                        break
        if len(available_villagers) > 0:
            for villager in available_villagers:
                pos = self.find_nearby_resources(villager,Type.Wood)
                if self.get_distance(villager.position, pos) > 1:
                        villager.move_towards(next_step, self.map_data)
                villager.gather_resources()
                available_villagers.remove(villager)        
    def get_available_villagers(self):
        available_villagers = []
        for villager in self.units: 
            if isinstance(villager, Villager):
                if isinstance(villager, Villager) and villager.is_idle():
                    available_villagers.append(villager)
        return available_villagers
                
    
    def allocate_villagers_for_construction(self, building):
        """
        Dynamically allocate Villagers to construct a building.

        Args:
        building: The building object being constructed.

        Returns:
        List of Villagers allocated for the construction.
        """
    # 1. Check building priority
        if building == TownHall:
            priority = "high"
        else:
            priority = "low"
    # 2. Define the number of Villagers based on priority
        if priority == "high":
            max_villagers = 4
        else:  # Low priority
            max_villagers = 2

    # 3. Identify available Villagers
        available_villagers = self.get_available_villagers()
        num_villagers = min(len(available_villagers), max_villagers)

    # 4. Assign Villagers
        assigned_villagers = available_villagers[:num_villagers]
        for villager in assigned_villagers:
<<<<<<< HEAD:models/Player/ai.py
            villager.start_building(building, num_villagers)

=======
            villager.start_building(building, len(assigned_villagers))
        
    
>>>>>>> origin/premain:models/Player/ai_begin_phase.py
        return assigned_villagers


    def reevaluate_construction(self, building, progress, current_villagers):
        """
        Reevaluate construction progress and reassign Villagers if needed.

        Args:
        building: The building under construction.
        progress: Current construction progress (percentage).
        current_villagers: List of Villagers already assigned.
        """
        # Check if construction is falling behind schedule
        if progress < 50 and len(current_villagers) < 4:
            additional_villagers = self.get_idle_villagers()[:2]  # Add 2 more Villagers if needed
            for villager in additional_villagers:
                villager.start_building(building, building.position)
    
    def construct_building(self, building_type, position):
        """
        Construct a building of the specified type at the given position.

        Args:
        building_type: The type of building to construct.
        position: The position on the map to construct the building.
        """
        
        building = building_type(position[0], position[1],self, self.game_state) 
        self.allocate_villagers_for_construction(building)
        self.map_data.place_building(building)
        self.buildings[building_type.__name__].append(building)
