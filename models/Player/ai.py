import random
from models.units.unit import unitStatus
from models.Player.strategy import Strategy  # Import Strategy from the appropriate module
from models.Buildings.farm import Farm
from models.Buildings.building  import Building
from models.Buildings.house import House
from models.Buildings.camp import Camp
from models.Buildings.barrack import Barrack
from models.Buildings.archery_range import Archery_Range
from models.Buildings.stable import Stable
from models.units.villager import Villager
from models.Buildings.town_center import Town_center
from models.Resources.Tile import Type

class IA:
    def __init__(self, player_id, game_state,strategy=Strategy.ECONOMIC):
        self.player_id = player_id
        self.strategy = strategy
        self.units = {
            "Villager": [u for u in game_state.model['units'] if u.unit_type == "Villager" and u.player_id == player_id] ,
            "Swordsman": [u for u in game_state.model['units'] if u.unit_type == "Swordsman" and u.player_id == player_id],
            "Archer": [u for u in game_state.model['units'] if u.unit_type == "Archer" and u.player_id == player_id],
            "Horseman": [u for u in game_state.model['units'] if u.unit_type == "Horseman" and u.player_id == player_id],
            "Attack": [],
        }
        self.game_state = game_state  # Full map data with obstacles and resources
        self.targets = None  # Store targets for each unit
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
            villager_position = (town_hall_position[0] + i, town_hall_position[1])
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

    def spawn_villager(self):
        """Spawn a new villager if the AI can afford it."""
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
    
    def find_nearby_targets(self, unit, enemy_units, range = 100):
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

    """"
    def collect_resource(self, resource_type) :
        # collect all villagers free for recolt
        villagers = [v for v in self.units["Villager"] if v.status == unitStatus.IDLE]

        # search the nearest resource of resource_type for each villager
        for v in villagers :
            if resource_type == 'Food':
                goal = self.find_nearby_building(v.position,"Farm")
            else:
                goal = self.find_nearby_resources(v, resource_type)
            if goal :
                if v.move_toward(goal, self.map_data) :
                    resource_gathered = v.collect(resource_type)
                    self.resources[resource_type] += resource_gathered 
                    print(f"{v.unit_type} gathered resource_type")
                else :
                    print(f"{v.unit_type} didn't gather resource_type")
                    """
           
    def find_nearby_building(self,pos, building_type):
        min_distance = 1000
        position = None
        for b in self.buildings[building_type]:
            distance = self.get_distance(pos, b.pos)
            if distance < min_distance and b.useable:
                min_distance = distance
                position = b.pos
        return position

    def find_nearby_dropoint(self, pos):
        town_pos = self.find_nearby_building(pos, "Town_center")
        camp_pos = self.find_nearby_building(pos, "Camp")
        if not camp_pos or self.get_distance(pos, town_pos) < self.get_distance(pos, camp_pos):
            return town_pos
        else:
            return camp_pos

    def gather_resource(self, unit, resource_type):
        pos = None
        unit.current_resource_type = resource_type
        if resource_type == 'Food':
            pos = self.find_nearby_building(unit.position,"Farm")
        else:
            pos = self.find_nearby_resources(unit, resource_type)
        if pos:
            unit.destination = pos
            self.change_unit_status(unit, unitStatus.GATHERING)

    def check_gathering(self):
        unit = self.get_unit_by_status("Villager", unitStatus.GATHERING)
        for u in unit:
            if u.carried_resources == u.resource_capacity:
                self.change_unit_status(u, unitStatus.RETURNING_RESOURCES)
                u.destination = self.find_nearby_dropoint(u.position)
    
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
        x = abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
        return x

    def find_path(self, unit, destination):
        #Find the shortest path to the destination using map data.
        return unit.find_path(destination, self.game_state.grid)
    
    def get_main_base(self):
        return self.buildings["Town_center"][0]
        
   
    """def execute_aggressive_strategy(self, #nb_attacks_consecutive):
        # Implement aggressive strategy logic here
        print("Executing aggressive strategy")
        # Example: Focus on training military units and attacking enemies
        villager_nb_min = 50
        building_nb_min = 5
        resource_level_min = 500
        resource_level = len(self.resources["food"]) + len(self.resources["wood"]) + len(self.resources["gold"])
        #non-military building/unit
        towncenter_nb = len(self.units["TownCenter"]
        house_nb = len(self.units["House"]
        farm_nb = len(self.units["Farm"]
        villager_nb = len(self.units["Villager"]
        nb_attacks_consecutive_max = 3
        
        if len(self.buildings["Barracks"]) < min_nb_building and self.resources["wood"] > 350 :
             self.construct_building("Barracks", self.find_nearby_available_position(pos,(3,3)))
        elif self.resources["wood"] < 350 :
            return# recolt resources
        else :
            if len(self.units["Horseman"]) < min_nb_horsemen and self.resources["food"] > 80 and self.resources["food"] > 20 : 
                return# create soldiers
            elif self.resources["food"] < 80 or self.resources["food"] < 20: 
                 return# recolt
            else: 
                if nb_attacks_consecutive < nb_attacks_consecutive_max :  
                    return    #attack
                #defense or spawn or recolt or build
                else :
                    if towncenter_nb < building_nb_min or house_nb < building_nb_min or farm_nb < building_nb_min or villager_nb < villager_nb_min or resource_level < resource_level_min :
                        #determine priority
                        l = list((towncenter_nb - building_nb_min, house_nb - building_nb_min or farm_nb - building_nb_min, villager_nb - villager_nb_min, resource_level - resource_level_min))
                        urg = min(l)
                        index = l.index(urg)
                        if index == 0 :
                            #construct towncenter
                        elif index == 1 :
                             #construct farm
                        elif index == 2 :
                             #construct house
                        elif index == 3 :
                             #spawn villager
                        else :
                             #collect ressource

                        #defense
                        
                             
                
    def nb_building(self) :
        return len(self.buildings["Barracks"]) + len(self.buildings["Town_center"]) + len(self.buildings["House"]) + len(self.buildings["Farm"]) + len(self.buildings["Stable"] + len(self.buildings["Archery_Range"] + len(self.buildings["Keep"] + len(self.buildings["Camp"]
    """ 
    def execute_aggressive_strategy(self):
        """
        military_units = []
        for unit_type in ["Archer", "Swordman", "Horseman", "Villager"]:
            military_units.extend(self.units.get(unit_type, []))
        self.spawn_villager()
        self.execute_attack_phase()"""
        if self.phase == 1:
            self.execute_phase_one()
        elif self.phase == 2:
            self.execute_phase_two()
        elif self.phase == 3:
            self.execute_attack_phase()
        

    def execute_phase_one(self):
        """
        Phase 1: Establish Military Infrastructure
        - Ensure Food Production
        - Construct Military Buildings
        """
        if len(self.units["Villager"]) < 20 :
            self.spawn_villager()     
        
        # Ensure Farms exist if food is limited
        if len(self.buildings['Farm']) <= 2 and self.resources['wood'] >= 100 and self.resources["food"] < 300:
            position = self.find_nearby_available_position(self.pos[0] + random.randint(-2,2)*5 , self.pos[1] + random.randint(-2,2)*5, (3, 3))
            if position and self.get_available_villagers():
                self.construct_building(Farm, position)
        
        # Construct Military Buildings
        if len(self.buildings["Barracks"]) < 1 and self.can_afford({"wood" : 175}) and self.get_available_villagers():
            x,y = self.buildings["Town_center"][random.randint(0,len(self.buildings["Town_center"]) - 1)].pos
            pos = self.find_nearby_available_position(x, y, (4,4))
            if pos:
                self.construct_building(Barrack, pos)
        
        if len(self.buildings["Stable"]) < 1 and self.can_afford({"wood" : 175}) and self.get_available_villagers():
            x,y = self.buildings["Town_center"][random.randint(0,len(self.buildings["Town_center"]) - 1)].pos
            pos = self.find_nearby_available_position(x, y, (4,4))
            if pos:
                self.construct_building(Stable, pos)
        
        if len(self.buildings["Archery_Range"]) < 1 and self.can_afford({"wood" : 175}) and self.get_available_villagers():
            x,y = self.buildings["Town_center"][random.randint(0,len(self.buildings["Town_center"]) - 1)].pos
            pos = self.find_nearby_available_position(x, y, (4,4))
            if pos:
                self.construct_building(Archery_Range, pos)
        
        self.allocate_villagers(food=0.4,wood=0.6, gold=0)
        
        # Transition to Phase 2 when military buildings exist
        if (len(self.buildings["Barracks"])) + len(self.buildings["Stable"]) + len(self.buildings["Archery_Range"]) > 2:
            self.phase = 2

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

    def execute_phase_two(self):
        """
        Phase 2: Train Army & Attack
        - Villager Allocation
        - Train a Balanced Army
        - Attack When Ready
        """
        if len(self.units["Villager"]) < 10:
            self.spawn_villager()   
        # Allocate Villagers: 60% Food, 30% Gold, 10% Flexible
        self.allocate_villagers(food=0.6,wood=0.05, gold=0.3)
        
        # Train a Balanced Army
        if self.resources["food"] >= 50 and self.resources["gold"] >= 20:
            for building_type in ["Barracks", "Stable", "Archery_Range"]:
                for building in self.buildings[building_type]:
                    if building.is_idle() and self.can_afford(building.unit_cost):
                        pos = self.find_nearby_available_position(building.pos[0], building.pos[1], (2,2))
                        if pos:
                            building.train_unit(pos, self.game_state)
                            self.deduct_resources(building.unit_cost)
                            print(f"AI is training a new {building.unit_type} at {pos}.")
                    elif building.training_time > 0:
                        unit = building.check_training(self.game_state)
                        if unit:
                            self.units[building.unit_type].append(unit)
        
        if self.check_mate():
            self.phase = 3
        
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
    
    def execute_defensive_strategy(self):
        # Implement defensive strategy logic here
        print("Executing defensive strategy")
        # Example: Focus on building defenses and protecting resources

    def execute_economic_strategy(self):
        if not self.is_base_secure():
            self.defend_base()
        if self.phase == 1:
            self.execute_begin_phase()
            if len(self.buildings["Town_center"]) >= 3:
                self.phase = 2
        elif self.phase == 2:
            if self.check_mate():
                self.launch_attack()
            self.execute_second_phase()
        if not self.is_base_secure():
            self.defend_base()
         
    def execute_begin_phase(self):
        # 0. Build Farm
        if len(self.buildings['Farm']) <= 3 and self.resources['wood'] >= 100:
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
        self.allocate_villagers(0.8,0.2,0)

        # 3. Build new Town Halls if conditions are met
        if len(self.buildings['Town_center']) < 3 and self.resources['wood'] >= 350:
            position = self.find_nearby_available_position(self.pos[0] - 5*random.randint(-2,2), self.pos[1] + 10*random.randint(1,3),(6,6))
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
            if (len(self.units["Villager"]) < 20 and
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
                if self.should_build_camp(node) and self.can_afford({"wood" : 100}) and self.get_available_villagers():
                    pos = self.find_nearby_available_position(node[0], node[1], (3, 3))
                    if pos:
                        self.construct_building(Camp, pos)

        # Build building to train army
        if len(self.buildings["Barracks"]) < 1 and self.can_afford({"wood" : 175}) and self.get_available_villagers():
            x,y = self.buildings["Town_center"][random.randint(0,len(self.buildings["Town_center"]) - 1)].pos
            pos = self.find_nearby_available_position(x, y, (4,4))
            if pos:
                self.construct_building(Barrack, pos)
        
        if len(self.buildings["Stable"]) < 1 and self.can_afford({"wood" : 175}) and self.get_available_villagers():
            x,y = self.buildings["Town_center"][random.randint(0,len(self.buildings["Town_center"]) - 1)].pos
            pos = self.find_nearby_available_position(x, y, (4,4))
            if pos:
                self.construct_building(Stable, pos)
        
        if len(self.buildings["Archery_Range"]) < 1 and self.can_afford({"wood" : 175}) and self.get_available_villagers():
            x,y = self.buildings["Town_center"][random.randint(0,len(self.buildings["Town_center"]) - 1)].pos
            pos = self.find_nearby_available_position(x, y, (4,4))
            if pos:
                self.construct_building(Archery_Range, pos)
        
        # Train a balanced army
        if self.resources["food"] >= 50 and self.resources["gold"] >= 20:
            for building_type in ["Barracks", "Stable", "Archery_Range"]:
                for building in self.buildings[building_type]:
                    if building.is_idle() and self.can_afford(building.unit_cost):
                        pos = self.find_nearby_available_position(building.pos[0], building.pos[1], (2,2))
                        if pos:
                            building.train_unit(pos, self.game_state)
                            self.deduct_resources(building.unit_cost)
                            print(f"AI is training a new {building.unit_type} at {pos}.")
                    elif building.training_time > 0:
                        unit = building.check_training(self.game_state)
                        if unit:
                            self.units[building.unit_type].append(unit)

       
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
            for unit_type in ["Archer", "Swordsman", "Horseman","Villager"]:
                military_units.extend(self.units.get(unit_type, []))
            base = self.get_main_base()
            if base:
                for unit in military_units:
                    if unit.status != unitStatus.BUILDING:
                        unit.move_toward((base.pos[0] + random.randint(-4,4), base.pos[1] + random.randint(-4,4)), self.map_data)
                self.execute_attack_phase()
                        
    def allocate_villagers(self, food = 0.6, wood = 0.2, gold = 0.2):
        
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
        
        if len(villager_farm) < food*len(self.units["Villager"]):
            if available_villagers:
                villager = available_villagers[0]
                villager_farm.append(villager)
                available_villagers.remove(villager)
        
        
        if len(villager_wood) < wood*len(self.units["Villager"]):
            if available_villagers:
                villager = available_villagers.pop(0)
                villager_wood.append(villager)
        
        if len(villager_gold) < gold*len(self.units["Villager"]) and self.phase > 1:
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
                nearby_enemies = [u for u in enemy_units if self.get_distance(u.position, base.position) < 20]
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
            if villager.current_resource_type == resource_type and villager.status == unitStatus.GATHERING:
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
        if not self.get_available_villagers:
            return False
        building = building_type(position)
        building.player_id = self.player_id
        self.deduct_resources(building.cost)
        self.buildings["In_construct"].append(building) 
        self.map_data.place_building(building)
        buiilder = self.allocate_villagers_for_construction(building)
        x = self.get_available_villagers()
        #print(f"AI is constructing a {building_type.__name__} at position {position} with {buiilder} there is {len(x)} villagers disponible in {len(self.units["Villager"])}.")
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
    
    def check_mate(self):
        """
        Check if the AI has enough units to launch an attack.
        The attack is performed if:
        1. The number of combat units surpasses a certain threshold.
        2. The total number of units significantly surpasses the opponent's unit count.

        :return: True if conditions for attack are met, False otherwise.
        """
        # Threshold for combat units to launch an attack
        combat_unit_threshold = 50
        
        # Get AI's combat unit count
        ai_combat_units = len(self.units["Swordsman"]) + len(self.units["Archer"]) + len(self.units["Horseman"])

        # Condition 1: Enough combat units
        if ai_combat_units >= combat_unit_threshold:
            #print(f"AI has {ai_combat_units} combat units, meeting the threshold of {combat_unit_threshold}.")
            return True

        # Get AI's total unit count
        ai_total_units = ai_combat_units + len(self.units["Villager"])

        # Get opponent's total unit count
        opponent_total_units = len(self.game_state.model["units"]) - ai_total_units

        

        # Condition 2: Total unit count far surpasses opponent
        unit_ratio = ai_total_units / max(1, opponent_total_units)  # Prevent division by zero
        if unit_ratio >= 1.5 and ai_total_units > 20:  # AI has at least twice as many units as the opponent
            #print(f"AI unit ratio ({unit_ratio:.2f}) surpasses opponent significantly.")
            return True

        # If neither condition is met, do not attack
        #print(f"AI does not meet attack conditions: {ai_combat_units} combat units, ratio {unit_ratio:.2f}.")
        return False

    def get_enemy_critical_point(self):
        """
    Identifies the nearest critical point to attack.
    Priority:
    1. Town Halls
    2. Military Buildings
    """
        critical_points = []

        # Collect enemy buildings
        enemy_buildings = self.get_enemy_buildings()

        # Prioritize Town Halls
        for building in enemy_buildings:
            if building.name == "Town_center":
                critical_points.append(building)

        # Add military buildings
        for building in enemy_buildings:
            if building.name in ["Barracks", "Stable", "Archery_Range"]:
                critical_points.append(building)

        # Sort by proximity to AI's main position
        ai_position = self.get_main_base().pos
        min_distance = float('inf')
        critpoint = None
        for p in critical_points:
            distance = self.get_distance(p.pos, ai_position)
            if distance < min_distance:
                critpoint = p
        
        # Return the nearest critical point
        return critpoint if critical_points else None

    def get_enemy_army(self):
        """
        Retrieves the enemy army's strength and composition.
        Returns:
        - A dictionary with counts of each unit type
        - Total strength score (optional)
        """
        enemy_units = [u for u in self.game_state.model['units'] if u.player_id != self.player_id]
        army_composition = {}
        total_strength = 0

        for unit in enemy_units:
            if unit.type not in army_composition:
                army_composition[unit.type] = 0
            army_composition[unit.type] += 1
            total_strength += unit.atk + unit.health  # Example strength calculation

        return {
        "composition": army_composition,
        "total_strength": total_strength
        }

    def get_enemy_buildings(self):
        building = [b for b in self.game_state.model['buildings'] if b.player_id != self.player_id]
        return building
    
    def launch_attack(self):
        """
        Launch an attack on the identified critical point.
        """
        # Identify the target critical point
        if not self.targets or self.targets.health <= 0:
            critical_point = self.get_enemy_critical_point()
            target = self.check_atk(critical_point)
            if target is None:
                print("No target")
                return  # No critical point to attack
            self.targets = target
        # Gather all available military units
        army_units = []
        for unit_type in ["Archer", "Swordsman", "Horseman","Villager"]:
            army_units.extend(self.units.get(unit_type, [])) 
        if not army_units:
            return  # No army available to attack
        target_pos = self.targets.pos if isinstance(self.targets, Building) else self.targets.position
        print(f"Target at {target_pos}")
        # Issue attack command to all units
        for unit in army_units:
            if unit.health <= 0:
                if unit in self.game_state.model['units']:
                    self.game_state.model['units'].remove(unit)
                self.units[unit.unit_type].remove(unit)
                self.map_data.get_tile(unit.position[0], unit.position[1]).unit.remove(unit)
                continue
            print(f"Unit of {self.player_id} at {unit.position}")
            if self.get_distance(unit.position, target_pos) > 1:
                unit.move_toward(target_pos, self.map_data)
                self.change_unit_status(unit, unitStatus.MOVING)
            else:
                unit.atk(self.targets)
                self.change_unit_status(unit, unitStatus.ATTACKING)
        # Optional: Update AI state to track the active attack
        
        print()
    def check_atk(self, nearby_targets):
        """
        Checks and prioritizes targets for an army to attack.

        Parameters:
        - army_position (tuple): The current position of the AI's army (x, y).
        - nearby_targets (list): A list of potential nearby targets (e.g., buildings, positions).
        - critical_point (tuple): The fallback critical point to attack if no nearby enemies.

        Returns:
        target (tuple): The selected target position to attack.
        """

    # Gather targets with enemy units
        enemy_targets = self.get_enemy_units_at(nearby_targets.pos)

    # If there are enemy targets, prioritize the nearest one
        if enemy_targets:
            return enemy_targets[0]
    # No enemy units nearby, fallback to the critical point
        return nearby_targets
    
    def get_enemy_units_at(self, position, radius = 10):
        """
        Searches for enemy units around a given position within a specified radius.

        Parameters:
        - position (tuple): The target position (x, y) to search around.
        - radius (int): The radius within which to search for enemy units.

        Returns:
        - list: A list of enemy units found within the radius.
        """
        x, y = position
        enemy_units = []

        # Iterate through all tiles within the square bounding the radius
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                search_x, search_y = x + dx, y + dy

                # Skip out-of-bound tiles
                if not self.map_data.is_within_bounds(search_x, search_y):
                    continue

                # Check the distance (Manhattan or Euclidean based on your game)
                if self.get_distance((x, y), (search_x, search_y)) <= radius:
                    # Retrieve any enemy units at this position
                    units_at_tile = self.map_data.get_tile(search_x, search_y).unit
                    for unit in units_at_tile:
                        if unit.player_id != self.player_id:  # Ensure it's an enemy unit
                            enemy_units.append(unit)
        print(enemy_units)
        return enemy_units

    def update(self):
        game_over, winner = self.endgame()
        if not game_over:
            # Continue normal gameplay
            if self.strategy == "AGGRESSIVE":
                self.execute_aggressive_strategy()
            elif self.strategy == Strategy.DEFENSIVE:
                self.execute_defensive_strategy()
            else:
                self.execute_economic_strategy()
        else:
            # Game is over, handle end state
            print(f"Game Over! Winner: Player {winner}")
            return True, winner
        
        return False, None
                 
    def remove_dead_units(self):
            unit_types = ["Villager", "Archer", "Horseman","Swordsman"]
            for unit_type in unit_types:
                if unit_type in self.units:
                # Find dead units
                    dead_units = [
                        unit for unit in self.units[unit_type] 
                        if unit.health <= 0
                ]
                    for dead_unit in dead_units:
                # Remove from AI controller
                        self.units[unit_type].remove(dead_unit)
                # Clear map position
                        if hasattr(dead_unit, 'position'):
                            x, y = dead_unit.position
                            #self.game_state.carte.grid[y][x].occupant = None
                # Remove from game state
                        self.game_state.model['units'].remove(dead_unit)
                # Update AI stats
                        #self.population -= 1        
                        print(f"{unit_type} died at position {dead_unit.position if hasattr(dead_unit, 'position') else 'unknown'}")

    def remove_dead_buildings(self):
            buildings_types=["Town_center","House","Farm","Barracks","Stable","Archery_Range","Keep","Camp"]
            for building_type in buildings_types:
                if building_type in self.buildings:
                # Find dead units
                    dead_buildings = [
                        building for building in self.buildings[building_type] 
                        if building.health <= 0
                ]
                    for dead_building in dead_buildings:
                        # Remove from AI controller
                        self.buildings[building_type].remove(dead_building)
                        # Clear map position
                        if hasattr(dead_building, 'position'):
                            x, y = dead_building.position
                            self.game_state.carte.grid[y][x].occupant = None
                        # Remove from game state
                        if dead_building in self.game_state.model['buildings']: 
                            self.game_state.model['buildings'].remove(dead_building)
                        # Update AI stats
                        #self.population -= 1        
                        print(f"{building_type} died at position {dead_building.position if hasattr(dead_building, 'position') else 'unknown'}")

    def execute_attack_phase(self):
        # Collect all military units
        military_units = []
        for unit_type in ["Archer", "Swordsman", "Horseman", "Villager"]:
            military_units.extend(self.units.get(unit_type, []))

        # Find all enemy units and buildings
        enemy_units = [u for u in self.game_state.model['units'] if u.player_id != self.player_id]
        enemy_buildings = [u for u in self.game_state.model['buildings'] if u.player_id != self.player_id]
        enemy_targets = enemy_units + enemy_buildings

        if not military_units or not enemy_targets:
            print("No military units or no enemies to attack.")
            return

        # Group military units into squads
        squad_size = 5
        squads = [military_units[i:i + squad_size] for i in range(0, len(military_units), squad_size)]
    
        for squad in squads:
            remaining_targets = enemy_targets.copy()
        
            for unit in squad:
                if not remaining_targets:
                    break
            
                # Find target for the unit
                unit.target = self.find_nearby_targets(unit, remaining_targets, 100)
                if not unit.target:
                    continue
            
                if not self.is_valid_target_position(unit.target.position):
                    print(f"Invalid target position {unit.target.position}. Skipping.")
                    continue

                # Move or attack based on distance
                distance_to_target = self.get_distance(unit.target.position, unit.position)
            
                if distance_to_target > unit.attack_range:
                    unit.move_toward(unit.target.position, self.game_state.carte)
                elif distance_to_target <= unit.attack_range:
                    unit.atk(unit.target)
                
                    # Check if target is destroyed
                    if unit.target.health <= 0:
                        print(f"Target at {unit.target.position} destroyed.")
                    
                        # Remove from appropriate list
                        if unit.target in enemy_units:
                            enemy_units.remove(unit.target)
                            self.game_state.model['units'].remove(unit.target)
                        elif unit.target in enemy_buildings:
                            enemy_buildings.remove(unit.target)
                            self.game_state.model['buildings'].remove(unit.target)
                    
                        remaining_targets.remove(unit.target)
            
                #Handle unit death
                if unit.health <= 0:
                    print(f"{unit.unit_type} died at {unit.position}.")
                    if unit in self.units[unit.unit_type]:
                        self.units[unit.unit_type].remove(unit)
                    if unit in self.game_state.model['units']:
                        self.game_state.model['units'].remove(unit)

        #print("Attack phase completed.")

    def is_valid_target_position(self, position):
        # Add checks to verify the target's position is valid
        try:
            x, y = position
            return (0 <= x < self.game_state.carte.largeur and 
                    0 <= y < self.game_state.carte.hauteur)
        except (TypeError, ValueError):
            return False

    def endgame(self):
        """
        Check if game is over and determine winner
        Returns: (game_over: bool, winner_id: int or None)
        """
        try:
            # Current player lost
            if len(self.buildings["Town_center"]) == 0:
                return True, self.get_opponent_id()
            
            # Other player lost
            other_players_tc = [
                b for b in self.game_state.model['buildings'] 
                if b.name == "Town_center" and b.player_id != self.player_id
            ]
            if len(other_players_tc) == 0:
                return True, self.player_id
            
            # Game continues
            return False, None
        
        except Exception as e:
            print(f"Error in endgame check: {e}")
            return False, None
    
    
