import random
from models.units.unit import unitStatus
from models.Player.strategy import Strategy  # Import Strategy from the appropriate module
from models.Buildings.farm import Farm
from models.Buildings.house import House
from models.Buildings.camp import Camp
from models.units.villager import Villager
from models.Buildings.town_center import Town_center
from models.Resources.Tile import Type

class IA:
    def __init__(self, player_id, game_state,strategy=Strategy.ECONOMIC):
        self.player_id = player_id
        self.strategy = strategy
        self.units = {
            "Villager": [u for u in game_state.model['units'] if u.unit_type == "Villager" and u.player_id == player_id] ,
            "Swordman": [u for u in game_state.model['units'] if u.unit_type == "Swordman" and u.player_id == player_id],
            "Archer": [u for u in game_state.model['units'] if u.unit_type == "Archer" and u.player_id == player_id],
            "Horseman": [u for u in game_state.model['units'] if u.unit_type == "Horseman" and u.player_id == player_id],
            "Attack": [],
        }
        self.game_state = game_state  # Full map data with obstacles and resources
        self.targets = {}  # Store targets for each unit
        self.resources = game_state.player_resources[player_id]  
        self.phase = 1
        self.buildings = {
            "Town_center": [b for b in game_state.model['buildings'] if b.name == "Town_center" and b.player_id == player_id],
            "House": [b for b in game_state.model['buildings'] if b.name == "House" and b.player_id == player_id],
            "Farm": [b for b in game_state.model['buildings'] if b.name == "Farm" and b.player_id == player_id],
            "Barracks": [b for b in game_state.model['buildings'] if b.name == "Barracks" and b.player_id == player_id],
            "Stable": [b for b in game_state.model['buildings'] if b.name == "Stable" and b.player_id == player_id],
            "Archery_Range": [b for b in game_state.model['buildings'] if b.name == "Archery_Range" and b.player_id == player_id],
            "Keep": [b for b in game_state.model['buildings'] if b.name == "Keep" and b.player_id == player_id],
            "Camp": [b for b in game_state.model['buildings'] if b.name == "Camp" and b.player_id == player_id],
            "In_construct": []
        }
        self.max_unit = 5
        self.map_data = game_state.carte
        self.pos = self.buildings["Town_center"][0].pos if self.buildings["Town_center"] else (0, 0)
        #self.initialize_starting_assets(20, 20)  # Example: Place starting assets at (5, 5)
        
    def initialize_starting_assets(self, x, y):
        
        self.resources["Food"] = 500
        self.resources["Wood"] = 350
        self.resources["Gold"] = 100
        
        self.pos = (x, y)
        town_hall_position = (x, y)  # You can choose a position on the map
        self.place_building(Town_center, town_hall_position)  # Place Town Hall on the map

        # Spawn 3 villagers near the Town Hall
        for i in range(3):
            villager_position = (town_center_position[0] + i, town_center_position[1])
            if self.game_state.carte.is_area_free(villager_position[0], villager_position[1],1,1):
                position = villager_position
            else:
                position = self.find_nearby_available_position(*villager_position, (1, 1))
            
            if position:
                villager = Villager(position[0],position[1],self.map_data)
                self.units["Villager"].append(villager)
                """self.game_state.all_unit.append(villager)"""
                self.game_state.carte.update_unit_position(villager, None, position)
            else:
                print("No valid position found for villager.")

    def can_afford(self, cost):
        return all(self.resources[res] >= cost[res] for res in cost)

    def deduct_resources(self, cost): 
        for res in cost:
            self.resources[res] -= cost[res]

    def find_nearby_available_position(self, x, y, building_size):
        """Find the nearest available position to build a building."""
        max_radius = max(self.game_state.carte.width, self.game_state.carte.height)  # Limit search within map bounds

        # Spiral outwards from the target location (x, y)
        for radius in range(1, max_radius):
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    new_x, new_y = x + 10  + dx, y +10 + dy
                    if self.game_state.carte.is_area_free(new_x, new_y, building_size[0], building_size[1]):
                        return new_x, new_y
                    
        return None  # Return None if no suitable area is found

    def place_building(self, building_type, initial_position):
        """Place a building of the specified type at or near the initial position."""
        x, y = initial_position
        building = building_type(initial_position)  # Create the building instance

        # Check if there's enough resources to build it
        if not self.can_afford(building.cost):
            print(f"Not enough resources to build {building_type.__name__}.")
            return

        # First, try to place the building at the initial position
        if self.game_state.carte.is_area_free(x, y, building.size[0], building.size[1]):
            self.game_state.carte.place_building(building)
            self.buildings[building.name].append(building)
            self.deduct_resources(building.cost)
            print(f"AI placed {building_type.__name__} at position ({x}, {y}).")
        else:
            # Find the nearest available position
            new_position = self.find_nearby_available_position(x, y, building.size)
            print(f"AI placed {building_type.__name__} near position ({new_position[0]}, {new_position[1]}).")
            if new_position:
                building.position = new_position
                self.game_state.carte.place_building(building)
                self.buildings[building.name].append(building)
                self.deduct_resources(building.cost)
                print(f"AI placed {building_type.__name__} near position ({new_position[0]}, {new_position[1]}).")
            else:
                print("No suitable position found to place the building.")

    def spawn_villager(self, Town_center):
        """Spawn a new villager if the AI can afford it."""
        villager_cost = {'Food': 50}  # Villager costs 50 Food
        if self.can_afford(villager_cost):
            # Deduct resources and spawn a new villager
            self.deduct_resources(villager_cost)
            villager_position = (town_hall.position[0], town_hall.position[1] + 1)
            if self.game_state.carte.is_area_free(villager_position[0], villager_position[1],1,1):
                position = villager_position
            else:
                position = self.find_nearby_available_position(*villager_position, (1, 1))
            
            if position:
                villager = Villager(position[0],position[1],self.game_state)
                self.units["Villager"].append(villager)
                #self.game_state.all_unit.append(villager)
                self.map_data.update_unit_position(villager, None, position)
                print(f"AI has spawned a new villager!")
        else:
            print(f"{self.player_id} cannot afford to spawn a villager.")
    
    def get_unit_by_status(self,type, status):
        units_with_status = []
        for unit in self.units[type]:
            if unit.status == status:  # Assuming unit has a 'status' attribute
                units_with_status.append(unit)
        return units_with_status
 
    def change_unit_status(self, unit, new_status):
        unit.status = new_status  
        print(f"Unit at {unit.position} status changed to {new_status}.")
        #else:
         #  print(f"Unit {unit} not found in AI's unit list.")

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
            if other_unit != unit and other_unit.player_id != unit.player_id:  # Avoid targeting itself or friendly units
                distance = self.get_distance(unit.position, other_unit.position)
                if distance <= range and distance < min_distance:
                    min_distance = distance
                    closest_target = other_unit
                    #print(f"{unit.unit_type} target {closest_target.unit_type}")

        return closest_target


    def collect_resource(self, unit, resource_type) :
        goal = self.find_nearby_resources(unit, resource_type)
        if goal :
            unit.move_toward(goal, self.map_data)
            resource_gathered = unit.collect(resource_type)
            self.resources[resource_type] += resource_gathered 
            print(f"{unit.unit_type} gathered resource_type")
        else :
            print(f"{unit.unit_type} didn't gather resource_type")
        
        
    def find_nearby_building(self,pos, building_type):
        min_distance = 1000
        position = None
        for b in self.buildings[building_type]:
            distance = self.get_distance(pos, b.pos)
            if distance < min_distance:
                min_distance = distance
                position = b.pos
        return position

    def gather_resource(self, unit, resource_type):
        pos = None
        unit.current_resource_type = resource_type
        if resource_type == 'Food':
            pos = self.find_nearby_building(unit.position,"Farm")
        else:
            pos = self.find_nearby_resources(unit, resource_type)
        unit.destination = pos
        self.change_unit_status(unit, unitStatus.GATHERING)

    def check_gathering(self):
        unit = self.get_unit_by_status("Villager", unitStatus.GATHERING)
        for u in unit:
            if u.carried_resources == u.resource_capacity:
                self.change_unit_status(u, unitStatus.RETURNING_RESOURCES)
                u.destination = self.find_nearby_building(u.position,"Town_center")
    
    def check_returning(self):
        unit = self.get_unit_by_status("Villager", unitStatus.RETURNING_RESOURCES)
        for u in unit:
            if self.get_distance(u.position, u.destination) <= 1:
                self.resources[u.current_resource_type.lower()] += u.carried_resources
                u.carried_resources = 0
                self.change_unit_status(u, unitStatus.IDLE)
    
    def find_nearby_resources(self, unit, resource_type):
        """
        Find nearby resources (F, W, G) for a specific unit.
        
        :param unit: The unit searching for resources.
        :param resource_type: The type of resource to search for ('F', 'W', 'G').
        :return: The nearest resource position or None.
        """
        closest_resource = None
        min_distance = float('inf')
        resource = self.map_data.get_resources()
        for r in resource:
            if self.map_data.get_tile(r[0], r[1]).resource.resource_type == resource_type:
                distance = self.get_distance(unit.position, r)
                if distance < min_distance:
                    closest_resource = r
                    min_distance = distance
        if closest_resource:
            print(f"{unit.unit_type} found {resource_type} at {closest_resource}")
        return closest_resource

    def find_nearby_available_position(self, x, y, building_size):
        #max_radius = max(self.game_state.largeur, self.game_state.hauteur)  
        max_radius = max(self.map_data.largeur, self.map_data.hauteur)  
        for radius in range(1, max_radius):
            for dx in range(-radius, radius + 1):
                 for dy in range(-radius, radius + 1):
                    new_x, new_y = x + dx, y + dy 
                    if 0 <= new_x < self.game_state.carte.largeur and 0 <= new_y < self.game_state.carte.hauteur:
                        if self.map_data.is_area_free(new_x, new_y, building_size[0], building_size[1]):
                            return new_x, new_y

        print("No valid position found for building.")
        return None

    """actiontype : Attack dans classe uml"""
    def make_decision(self, all_units):
    
        self.control_buildings()
        
        for unit in self.units["Villager"]:
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
        return abs(pos1[0] - pos2[0]) + abs(pos2[1] - pos2[1])

    def find_path(self, unit, destination):
        #Find the shortest path to the destination using map data.
        return unit.find_path(destination, self.game_state.grid)
    
    def get_main_base(self):
        town_centers = [b for b in self.buildings if b.__class__.__name__ == "Town_center"]
        return town_centers[0] if town_centers else None
    
    def execute_aggressive_strategy(self):
        # Implement aggressive strategy logic here
        print("Executing aggressive strategy")
        # Example: Focus on training military units and attacking enemies

    def execute_defensive_strategy(self):
        # Implement defensive strategy logic here
        print("Executing defensive strategy")
        # Example: Focus on building defenses and protecting resources

    def execute_economic_strategy(self):
        if self.phase == 1:
            self.execute_begin_phase()
            if len(self.buildings["Town_center"]) >= 4:
                self.phase = 2
        elif self.phase == 2:
            self.execute_second_phase()
            
    def execute_begin_phase(self):
        # 0. Build Farm
        if len(self.buildings['Farm']) <= 4 and self.resources['wood'] >= 100:
            position = self.find_nearby_available_position(self.pos[0] + random.randint(-2,2)*5 , self.pos[1] + random.randint(-2,2)*5, (3, 3))
            if position and self.get_available_villagers():
                self.construct_building(Farm, position)
        
        # 1. Train Villagers if possible
        for town_hall in self.buildings['Town_center']:
            if town_hall.is_idle() and self.resources['food'] >= 50:
                pos = self.find_nearby_available_position(town_hall.pos[0], town_hall.pos[1], (4, 4))
                town_hall.train_villager(pos,self.game_state)
                print(f"AI is training a new Villager at {pos}.")
                self.deduct_resources({'food': 50})
            elif town_hall.training_time > 0:
                villa = town_hall.check_training(self.game_state)
                if villa:
                    self.units["Villager"].append(villa)

        # 2. Allocate Villagers to resources
        self.allocate_villagers()

        # 3. Build new Town Halls if conditions are met
        if len(self.buildings['Town_center']) < 4 and self.resources['wood'] >= 350:
            position = self.find_nearby_available_position(self.pos[0] + 20, self.pos[1],(6,6))
            if position and self.get_available_villagers():
                self.construct_building(Town_center, position)

        if len(self.units) + 5 < self.max_unit:
            if self.resources['wood'] >= 25:
                position = self.find_nearby_available_position(self.pos[0], self.pos[1],(2,2))
                if position:
                    self.construct_building('House',position)
            else:
                self.balance_resources()
        # 4. Adjust strategy if resources are unbalanced
        #self.balance_resources()
        for building in self.buildings["In_construct"]:
            #print(f"Building {building.name} at {building.pos} is building complete in {building.construction_time} turns.")
            building.check_construction()   
            if building.useable:
                self.buildings["In_construct"].remove(building)
                self.game_state.model['buildings'].append(building)
                for villager in building.builder:
                    self.change_unit_status(villager, unitStatus.IDLE)
        for list in self.units.values():
            for unit in list:
                unit.update()  
                
        self.check_returning()
        self.check_gathering()
    
    def execute_second_phase(self):

        # Generate Villagers until 100
        for town_center in self.buildings["Town_center"]:
            if (len(self.units["Villager"]) < 100 and
                    self.resources["food"] >= 50 and town_center.is_idle()):
                pos = self.find_nearby_available_position(town_center.pos[0],town_center.pos[1], (2,2))
                town_center.train_villager(pos, self.game_state)
                self.deduct_resources({'food': 50})
                print(f"AI is training a new Villager at {pos}.")
            elif town_center.training_time > 0:
                villa = town_center.check_training(self.game_state)
                if villa:
                    self.units["Villager"].append(villa)
        
        #  Allocate Villagers to resources
        self.allocate_villagers()
        
        # Gradually transition Villagers to collect Gold
        gold_villagers = self.count_villagers_collecting("Town_center")
        if gold_villagers < len(self.units["Villager"]) * 0.3:  # Target 30% collecting Gold
            for villager in self.units["Villager"]:
                if villager.current_resource_type == "Wood":
                    villager.collect_resource("Gold")

        # Build Camps near resource nodes
        for resource_type in ["Wood", "Gold"]:
            for node in self.resource_nodes(resource_type):
                if self.should_build_camp(node):
                    pos = self.find_nearby_available_position(node[0], node[1], (3, 3))
                    if pos:
                        self.construct_building(Camp, pos)

        # Train a balanced army
        if self.resources["food"] >= 50 and self.resources["gold"] >= 20:
            for building_type in ["Barracks", "Stable", "Archery_Range"]:
                for building in self.buildings[building_type]:
                    if building.is_idle():
                        building.train_unit(self.next_unit_type(building_type))

        # Build Farms in advance
        if len(self.buildings["Farm"]) < 5:
            pos = self.buildings["Town_center"][random.randint(1,len(self.buildings["Town_center"]))]
            self.construct_building("Farm", self.find_nearby_available_position(pos,(3,3)))

        if not self.is_base_secure():
            self.defend_base()
        
        # Update unit and building state
        for building in self.buildings["In_construct"]:
            #print(f"Building {building.name} at {building.pos} is building complete in {building.construction_time} turns.")
            building.check_construction()   
            if building.useable:
                self.buildings["In_construct"].remove(building)
                self.game_state.model['buildings'].append(building)
                for villager in building.builder:
                    self.change_unit_status(villager, unitStatus.IDLE)
        for list in self.units.values():
            for unit in list:
                unit.update()  
        self.check_returning()
        self.check_gathering()
        
    def defend_base(self):
            military_units = []
            for unit_type in ["Archer", "Swordman", "Horseman","Villager"]:
                military_units.extend(self.units.get(unit_type, []))
            base = self.get_main_base()
            if base:
                for unit in military_units:
                     unit.move_toward((base.pos[0] + random.randint(-4,4), base.pos[1] + random.randint(-4,4)))
                        
    def allocate_villagers(self):
        
        available_villagers = self.get_available_villagers()
        villager_gather = self.get_unit_by_status("Villager", unitStatus.GATHERING)
        villager_farm =[]
        villager_wood =[]
        villager_gold =[]
        for v in villager_gather:
            if v.current_resource_type == "Food":
                villager_farm.append(v)
            elif v.current_resource_type == "Wood":
                villager_wood.append(v)
            else:
                villager_gold.append(v)
        
        if len(villager_farm) < 4:
            if available_villagers:
                villager = available_villagers[0]
                villager_farm.append(villager)
                available_villagers.remove(villager)
        
        
        if len(villager_wood) < 3:
            if available_villagers:
                villager = available_villagers.pop(0)
                villager_wood.append(villager)
        
        if len(villager_gold) < 3 and self.phase > 1:
            if available_villagers:
                villager = available_villagers.pop(0)
                villager_gold.append(villager)
        
        for villager in villager_farm:
            if villager.status == unitStatus.IDLE:
                self.gather_resource(villager,"Food")
                         
        for villager in villager_wood:
            if villager.status == unitStatus.IDLE:
                self.gather_resource(villager, "Wood")
        
        for villager in villager_gold:
            if villager.status == unitStatus.IDLE:
                self.gather_resource(villager, "Gold")
             
    def get_available_villagers(self):
        available_villagers = self.get_unit_by_status("Villager", unitStatus.IDLE)
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
        if building.name == "Town_center":
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
        building.building(assigned_villagers)
        for villager in assigned_villagers:
            villager.start_building(building, len(assigned_villagers))
            self.change_unit_status(villager, unitStatus.BUILDING)
            if villager.position != building.pos:
                villager.move_toward(building.pos, self.map_data)
        
    
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
            additional_villagers = self.get_available_villagers[:2]  # Add 2 more Villagers if needed
            for villager in additional_villagers:
                villager.start_building(building, building.position)
    
    def count_villagers_collecting(self, resource_type):
        """
        Count the number of villagers collecting a specific resource.

        :param resource_type: The type of resource to count (e.g., "Food", "Wood", "Gold").
        :return: The number of villagers collecting the specified resource.
        """
        count = 0
        for villager in self.units["Villager"]:
            if villager.current_resource_type == resource_type:
                count += 1
        return count

    def is_base_secure(self):
        # Vérifie si la base est menacée
            enemy_units = [u for u in self.game_state.model['units'] if u.player_id != self.player_id]
            base = self.get_main_base()
            if base:
                nearby_enemies = [u for u in enemy_units if self.get_distance(u.position, base.position) < 10]
                return len(nearby_enemies) == 0
            return False

    def resource_nodes(self, resource_type):
        """
        Get a list of resource nodes of a specific type.

        :param resource_type: The type of resource to find (e.g., "Food", "Wood", "Gold").
        :return: A list of resource nodes of the specified type.
        """
        nodes = set()
        """
        for y, row in enumerate(self.map_data.grille):
            for x, tile in enumerate(row):
                if tile.resource != None:
                    if tile.resource.resource_type == resource_type:
                        nodes.add((x, y))
                        """
        
        for villager in self.units["Villager"]:
            if villager.current_resource_type == resource_type:
                pos = villager.position
                nodes.add(pos)
        
        return nodes
             
    def get_available_villagers(self):
        available_villagers = self.get_unit_by_status("Villager", unitStatus.IDLE)
        return available_villagers
    
    def construct_building(self, building_type, position):
        """
        Construct a building of the specified type at the given position.

        Args:
        building_type: The type of building to construct.
        position: The position on the map to construct the building.
        """
        building = building_type(position)
        building.player_id = self.player_id
        self.deduct_resources(building.cost)
        self.buildings["In_construct"].append(building) 
        self.map_data.place_building(building)
        buiilder = self.allocate_villagers_for_construction(building)
        x = self.get_available_villagers()
        print(f"AI is constructing a {building_type.__name__} at position {position} with {buiilder} there is {len(x)} villagers disponible in {len(self.units["Villager"])}.")
        self.buildings[building.name].append(building)

    def should_build_camp(self, node):
        """
        Determine if a Camp should be built near a resource node.

        Args:
        node: The resource node to evaluate.

        Returns:
        True if a Camp should be built, False otherwise.
        """
        min_distance = 100
        for town_center in self.buildings["Town_center"]:
            distance = self.get_distance(town_center.pos, node)
            min_distance = min(distance, min_distance)
        for cam in self.buildings["Camp"]:
            distance = self.get_distance(cam.pos, node)
            min_distance = min(min_distance, distance)
            
        distance_threshold = 10  # Define a threshold distance

        return min_distance > distance_threshold
        
    def update(self):
        """"""
        if self.strategy == Strategy.AGGRESSIVE:
            self.execute_aggressive_strategy()
        elif self.strategy == Strategy.DEFENSIVE:
            self.execute_defensive_strategy()
        else:
            self.execute_economic_strategy()
        
        
        #for villager in self.units["Villager"]:
         #   print(villager.status)
              
