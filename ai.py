from unit.unit import Unit 
from unit.villager import Villager
from building.town_hall import TownHall
from resource.tile import Type  


class IA:
    def __init__(self, name, map_data):
        self.name = name
        self.units = []  
        self.map_data = map_data  # Full map data with obstacles and resources
        self.targets = {}  # Store targets for each unit
        self.resources = {"Food": 0, "Wood": 0, "Gold": 0}  
        self.buildings = []
        self.max_unit = 5
        
    def initialize_starting_assets(self, x, y):
        
        self.resources["Food"] = 500
        self.resources["Wood"] = 350
        self.resources["Gold"] = 100
        
        town_hall_position = (x, y)  # You can choose a position on the map
        self.place_building(TownHall, town_hall_position)  # Place Town Hall on the map

        # Spawn 3 villagers near the Town Hall
        for i in range(3):
            villager_position = (town_hall_position[0] + i, town_hall_position[1])
            if self.map_data.is_area_free(villager_position[0], villager_position[1],1,1):
                position = villager_position
            else:
                position = self.find_nearby_available_position(*villager_position, (1, 1))
            
            if position:
                villager = Villager(position[0],position[1],self.map_data)
                self.units.append(villager)
                self.map_data.all_unit.append(villager)
                self.map_data.update_unit_position(villager, None, position)
            else:
                print("No valid position found for villager.")

    def can_afford(self, cost):
        return all(self.resources[res] >= cost[res] for res in cost)

    def deduct_resources(self, cost): 
        for res in cost:
            self.resources[res] -= cost[res]

    def find_nearby_available_position(self, x, y, building_size):
        """Find the nearest available position to build a building."""
        max_radius = max(self.map_data.width, self.map_data.height)  # Limit search within map bounds

        # Spiral outwards from the target location (x, y)
        for radius in range(1, max_radius):
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    new_x, new_y = x + dx, y + dy
                    if self.map_data.is_area_free(new_x, new_y, building_size[0], building_size[1]):
                        return new_x, new_y
                    
        return None  # Return None if no suitable area is found

    def place_building(self, building_type, initial_position):
        """Place a building of the specified type at or near the initial position."""
        x, y = initial_position
        building = building_type(initial_position[0], initial_position[1], "", self.map_data)  # Create the building instance

        # Check if there's enough resources to build it
        if not self.can_afford(building.cost):
            print(f"Not enough resources to build {building_type.__name__}.")
            return

        # First, try to place the building at the initial position
        if self.map_data.is_area_free(x, y, building.size[0], building.size[1]):
            self.map_data.place_building(building)
            self.buildings.append(building)
            self.deduct_resources(building.cost)
            print(f"AI placed {building_type.__name__} at position ({x}, {y}).")
        else:
            # Find the nearest available position
            new_position = self.find_nearby_available_position(x, y, building.size)
            if new_position:
                building.position = new_position
                self.map_data.place_building(building)
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
            if self.map_data.is_area_free(villager_position[0], villager_position[1],1,1):
                position = villager_position
            else:
                position = self.find_nearby_available_position(*villager_position, (1, 1))
            
            if position:
                villager = Villager(position[0],position[1],self.map_data)
                self.units.append(villager)
                self.map_data.all_unit.append(villager)
                self.map_data.update_unit_position(villager, None, position)
                print(f"AI has spawned a new villager!")
        else:
            print(f"{self.name} cannot afford to spawn a villager.")

    def manage_resources(self):
        """Manage resource gathering by villagers."""
        for unit in self.units:
            if isinstance(unit, Villager):
                unit.collect_resources(self)

    def control_buildings(self):
        """Control the AI's buildings (e.g., TownHall to spawn villagers)."""
        for building in self.buildings:
            if isinstance(building, TownHall):
                # AI decision to spawn a villager
                if len(self.units) < 10 and self.resources["Food"] > 50:  # Example: If AI has fewer than 10 units
                    self.spawn_villager(building)

    def set_target(self, unit, target):
        """
        Set a target for a specific unit.
        """
        self.targets[unit] = target
    
    def find_nearby_targets(self, unit, all_units, range = 20):
        """
        Find a nearby target within the given range for a specific unit.
        
        :param unit: The unit searching for a target.
        :param all_units: A list of all units on the map.
        :param range: The range within which the unit can search for targets.
        :return: The nearest target if found, or None.
        """
        closest_target = None
        min_distance = float('inf')

        for other_unit in all_units:
            if other_unit != unit and other_unit not in self.units:  # Avoid targeting itself or friendly units
                distance = self.get_distance(unit.position, other_unit.position)
                if distance <= range and distance < min_distance:
                    min_distance = distance
                    closest_target = other_unit
                    #print(f"{unit.unit_type} target {closest_target.unit_type}")

        return closest_target

    def gather_resource(self, unit):

        x, y = unit.position[0], unit.position[1]
        resource_type = self.map_data[y][x]  # Check the map tile the unit is on
        
        if resource_type == 'F':
            self.resources["Food"] += 1 
            print(f"{unit.unit_type} gathered Food. Total: {self.resources['Food']}")
            self.map_data[y][x] = ' '  # Clear the resource from the map after gathering
        elif resource_type == 'W':
            self.resources["Wood"] += 1 
            print(f"{unit.unit_type} gathered Wood. Total: {self.resources['Wood']}")
            self.map_data[y][x] = ' '
        elif resource_type == 'G':
            self.resources["Gold"] += 1 
            print(f"{unit.unit_type} gathered Gold. Total: {self.resources['Gold']}")
            self.map_data[y][x] = ' '

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
        for y, row in enumerate(self.map_data.grid):
            for x, tile in enumerate(row):
                if tile.get_type() == resource_type:
                    distance = self.get_distance(unit.position, (x, y))
                    if distance < min_distance:
                        min_distance = distance
                        closest_resource = (x, y)
        print(f"{unit.unit_type} found {resource_type} at {closest_resource}")
        return closest_resource

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
                        unit.move_towards(next_step, self.map_data)
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
                            unit.move_towards(next_step, self.map_data)
                        else:
                            # If the unit is already on the resource tile, gather it
                            self.gather_resource(unit)

    def get_distance(self, pos1, pos2):
        #Get the Manhattan distance between two positions.
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def find_path(self, unit, destination):
        #Find the shortest path to the destination using map data.
        return unit.find_path(destination, self.map_data.grid)

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
        for building in self.buildings:
            if building is TownHall:
                for villager in available_villagers:
                    if villager.position != building.position:
                        villager.move_towards(building.position)
                    else:
                        villager.gather_resources()
                    available_villagers.remove(villager)
                    break
            for _ in range(5):
                for villager in available_villagers:
                    pos = self.find_nearby_resources(villager,Type.Food)
                    if villager.position != pos:
                        villager.move_towards(pos)
                    else:
                        villager.gather_resources()
                    available_villagers.remove(villager)
                    break
        if len(available_villagers) > 0:
            for villager in available_villagers:
                pos = self.find_nearby_resources(villager,Type.Wood)
                if self.get_distance(villager.position, pos) > 1:
                    villager.move_towards(pos)
                else:
                    villager.gather_resources()
                available_villagers.remove(villager)        
                    
    def get_available_villagers(self):
        available_villagers = []
        for villager in self.units: 
            if villager is Villager:
                if villager.is_idle():
                    available_villagers.append(villager)
        return available_villagers
                
    
    def allocate_villagers_for_construction(self, building, building_pos, ai_resources):
        """
        Dynamically allocate Villagers to construct a building.

        Args:
        building: The building object being constructed.
        building_pos: Position of the building on the map.
        ai_resources: The AI's current resource state.

        Returns:
        List of Villagers allocated for the construction.
        """
    # 1. Check building priority
        priority = building.priority  # Assume each building has a priority attribute (e.g., high, medium, low).

    # 2. Define the number of Villagers based on priority
        if priority == "high":
            max_villagers = 6
        elif priority == "medium":
            max_villagers = 4
        else:  # Low priority
            max_villagers = 2

    # 3. Identify available Villagers
        available_villagers = self.get_available_villagers()
        num_villagers = min(len(available_villagers), max_villagers)

    # 4. Assign Villagers
        assigned_villagers = available_villagers[:num_villagers]
        for villager in assigned_villagers:
            villager.start_building(building, building_pos)

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
