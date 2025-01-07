from unit.unit import Unit 
from unit.villager import Villager
from building.town_hall import TownHall


class IA:
    def __init__(self, name, map_data):
        self.name = name
        self.units = []  
        self.map_data = map_data  # Full map data with obstacles and resources
        self.targets = {}  # Store targets for each unit
        self.resources = {"Food": 0, "Wood": 0, "Gold": 0}  
        self.buildings = []
        
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
        
        :param unit: The unit to assign a target to.
        :param target: The target unit or resource for the given unit.
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
            self.resources["Food"] += 1 "300"
            print(f"{unit.unit_type} gathered Food. Total: {self.resources['Food']}")
            self.map_data[y][x] = ' '  # Clear the resource from the map after gathering
        elif resource_type == 'W':
            self.resources["Wood"] += 1 "100"
            print(f"{unit.unit_type} gathered Wood. Total: {self.resources['Wood']}")
            self.map_data[y][x] = ' '
        elif resource_type == 'G':
            self.resources["Gold"] += 1 
            print(f"{unit.unit_type} gathered Gold. Total: {self.resources['Gold']}")
            self.map_data[y][x] = ' '

    def find_nearby_resources(self, unit):
        """
        Find nearby resources (F, W, G) for a specific unit.
        
        :param unit: The unit searching for resources.
        :return: The nearest resource position or None.
        """
        closest_resource = None
        min_distance = float('inf')
        resource_tiles = ['F', 'W', 'G']
        
        # Scan the map for nearby resources
        for y, row in enumerate(self.map_data.grid):
            for x, tile in enumerate(row):
                if tile in resource_tiles:
                    distance = self.get_distance(unit.position, (x, y))
                    if distance < min_distance:
                        min_distance = distance
                        closest_resource = (x, y)
        
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
