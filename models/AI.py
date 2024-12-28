import json
from collections import DefaultDict
from .unit import *
from .villager import *

class AI:
    def __init__(self, game_time, map, resource_man):
        self.game_time = game_time
        self.map = map
        self.resource_man = resource_man
        self.previous_time = 0
        self.created_tc = False
        self.created_bar = False
        self.created_arc = False
        self.AI_unit = []
        self.AI_villager = []
        self.AI_batiment = []
        self.age = 1
        with open(AI_action_JSONfile) as f:
            self.data = json.load(f)
        self.function_list = [
            self.AI_construct_Towncenter, self.AI_construct_Barracks, self.AI_construct_Archery,
            self.create_Archer, self.create_villager, self.get_resource, 
            self.AI_construct_Stable, self.create_Cavalier, self.all_attack
        ]
        self.towncenter = self.AI_construct_Towncenter(5, 10)

        self.all_in = False

    def read_file(self):
        action_line = self.f.readline()
        if action_line == '':
            action_line = ' - -(0,0)'
        action_line = action_line.rsplit("\n")
        action = action_line[0].split("-")
        li = action[2][1:-1].split(',')
        li = (int(li[0]), int(li[1]))
        action[2] = li
        return action
        
"""pourquoi retourner le town center ?"""
"""qu'est-ce que self.map.buildings[x][y] ?"""
"""temps de construction ?"""
"""1 méthode AI_construct() plutôt qu'une pouchaque type de bâtiment (voir IA Khanh)"""
    def AI_construct_Towncenter(self, x, y):
        if not self.map.world[x][y]["collision"]:
            ent = TownCenter((x, y), self.resource_man, "Red", True)
            self.map.add_entity(ent)
            self.AI_batiment.append(ent)
            self.map.buildings[x][y] = ent
            self.created_tc = True
            return ent
        else:
            if (0 < y < 49):
                return self.AI_construct_Towncenter(x, y + 1)
            elif (0 < x < 49):
                return self.AI_construct_Towncenter(x + 1, y)

    def AI_construct_Barracks(self, x, y):
        if not self.map.world[x][y]["collision"]:
            ent = Barracks((x, y), self.resource_man, "Red", False)
            self.map.add_entity(ent)
            self.AI_batiment.append(ent)
            self.map.buildings[x][y] = ent
            self.created_bar = True
        elif (not self.map.world[x][y+1]["collision"]) or (not self.map.world[x+1][y]["collision"]):
            if not self.map.world[x][y+1]["collision"]:
                self.AI_construct_Barracks(x, y + 1)
            elif not self.map.world[x+1][y]["collision"]:
                self.AI_construct_Barracks(x + 1, y)
        else:
            if not self.map.world[x][y+2]["collision"]:
                self.AI_construct_Barracks(x, y + 2)
            else:
                self.AI_construct_Barracks(x + 2, y)

    def AI_construct_Archery(self, x, y):
        if not self.map.world[x][y]["collision"]:
            ent = Archery((x, y), self.resource_man, "Red", False)
            self.map.add_entity(ent)
            self.AI_batiment.append(ent)
            self.map.buildings[x][y] = ent
            self.created_arc = True
        elif (not self.map.world[x][y+1]["collision"]) or (not self.map.world[x+1][y]["collision"]):
            if not self.map.world[x][y+1]["collision"]:
                self.AI_construct_Archery(x, y + 1)
            elif not self.map.world[x+1][y]["collision"]:
                self.AI_construct_Archery(x + 1, y)
        else:
            if not self.map.world[x][y+2]["collision"]:
                self.AI_construct_Archery(x, y + 2)
            else:
                self.AI_construct_Archery(x + 2, y)

    def AI_construct_Stable(self, x, y):
        if not self.map.world[x][y]["collision"]:
            ent = Stable((x, y), self.resource_man, "Red", False)
            self.map.add_entity(ent)
            self.AI_batiment.append(ent)
            self.map.buildings[x][y] = ent
            self.created_arc = True
        elif (not self.map.world[x][y+1]["collision"]) or (not self.map.world[x+1][y]["collision"]):
            if not self.map.world[x][y+1]["collision"]:
                self.AI_construct_Stable(x, y + 1)
            elif not self.map.world[x+1][y]["collision"]:
                self.AI_construct_Stable(x + 1, y)
        else:
            if not self.map.world[x][y+2]["collision"]:
                self.AI_construct_Stable(x, y + 2)
            else:
                self.AI_construct_Stable(x + 2, y)

    def find_resource(self):
        vill_dict = DefaultDict(list)
        i = 0
        for villager in self.AI_villager:
            vill_list = []

            vill_list.append(self.get_distance(villager, "Wood"))
            vill_list.append(self.get_distance(villager, "Food"))
            vill_list.append(self.get_distance(villager, "Gold"))
            vill_dict[str(i)] = vill_list
            i += 1
        return vill_dict

    def get_resource(self, resource):
        dict_resource = self.find_resource()
        if not dict_resource:
            return

     
        min_distance = 100 
        villager_pos = (-1, -1, -1)

        for i in dict_resource.keys():
            if self.AI_villager[int(i)].in_work: 
                continue
          
            resource_index = self.get_resource_index(resource)
            if dict_resource[i][resource_index][2] < min_distance:
                min_distance = dict_resource[i][resource_index][2]
                villager_pos = (dict_resource[i][resource_index][0], dict_resource[i][resource_index][1], i)

        if villager_pos == (-1, -1, -1):
            return

        villager = self.AI_villager[int(villager_pos[2])]
        if villager.map.world[villager_pos[0] + 1][villager_pos[1]]["collision"]:
            self.get_new_resource(resource, 1)
            self.get_new_resource(resource, 2)
            self.get_new_resource(resource, 3)
        else:
            villager.set_target((villager_pos[0] + 1, villager_pos[1]))  
            villager.in_work = True
            self.map.list_mining.append(self.map.world[villager_pos[0]][villager_pos[1]])
            self.map.world[villager_pos[0]][villager_pos[1]]["mining_team"] = "Red"
            self.map.events.getting_resource()
            self.map.mining = True

    def get_resource_index(self, resource):
    
        resource_map = {
            "Wood": 1,
            "Food": 2,
            "Gold": 3
        }
        return resource_map.get(resource, -1)

    def get_distance(self, villager, resource_type):

        resource_positions = self.get_resource_positions(resource_type)
        min_distance = float("inf")
        nearest_pos = None

        for pos in resource_positions:
            distance = self.calculate_distance(villager.position, pos)
            if distance < min_distance:
                min_distance = distance
                nearest_pos = pos

        return nearest_pos + (min_distance,)

    def calculate_distance(self, point1, point2):
      
        return ((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2) ** 0.5

    def get_resource_positions(self, resource_type):
        positions = []
        for row in self.map.world:
            for cell in row:
                if resource_type == "Wood" and cell["resource"] == "Wood":
                    positions.append((cell["x"], cell["y"]))
                elif resource_type == "Food" and cell["resource"] == "Food":
                    positions.append((cell["x"], cell["y"]))
                elif resource_type == "Gold" and cell["resource"] == "Gold":
                    positions.append((cell["x"], cell["y"]))
            
        return positions
    # Other methods remain the same, up to the auto_attack method...
    def get_new_distance(self, villager, type_resource):
         distance_list = []
          for x in range(self.map.grid_size_x):
            for y in range(self.map.grid_size_y):
                if self.map.world[x][y].tile_type == type_resource:  
                  l = ((villager.position[0] - x) ** 2 + (villager.position[1] - y) ** 2) ** (1 / 2)
                  distance_list.append((l, x, y))  
         return sorted(distance_list)

def find_new_resource(self):
    vill_dict = DefaultDict(list)
    for i, villager in enumerate(self.AI_villager):
        vill_dict[str(i)] = [
            self.get_new_distance(villager, "Wood"),
            self.get_new_distance(villager, "Food"),
            self.get_new_distance(villager, "Gold"),
        ]
    return vill_dict

def get_new_resource(self, resource, i_th_time):
  
    dict_resource = self.find_new_resource()
    if not dict_resource:
        return

    min_distance = 100 
    villa_pos = (-1, -1, -1)  
    
    for i, resource_list in dict_resource.items():
        if self.AI_villager[int(i)].in_work:  
            continue
        
        resource_idx = {"Wood": 0, "Food": 1, "Gold": 2}.get(resource)
        if resource_idx is not None:
            distance, x, y = resource_list[resource_idx][i_th_time]
            if distance < min_distance:
                min_distance = distance
                villa_pos = (x, y, i)

    if villa_pos == (-1, -1, -1):
        return

  
    villager = self.AI_villager[int(villa_pos[2])]
    target_x, target_y = villa_pos[0] + 1, villa_pos[1]  


    if villager.map.get_tile(target_x, target_y).collision:
        return

 
    villager.set_target((target_x, target_y))
    villager.in_work = True 
    self.map.list_mining.append(self.map.get_tile(villa_pos[0], villa_pos[1]))
    self.map.get_tile(villa_pos[0], villa_pos[1]).mining_team = "Red"
    self.map.events.getting_resource() 
    self.map.mining = True


    def auto_attack(self):
        # Iterate through all AI units
        for soldier in self.AI_unit:
            atk_range = soldier.get_attack_range()  # Get the attack range of the soldier
            for target_pos in atk_range:
                # Check if the target is within range
                target_soldier = self.map.units.get(target_pos[0], {}).get(target_pos[1])
                if target_soldier and target_soldier.team == "Blue":  # Ensure target is from the "Blue" team
                    self.map.list_units_atk.append((soldier, target_soldier))  # Add the attack pair to the list

    def all_attack(self, x, y):
        target = None
        # Find the potential targets based on their coordinates and the specified names
        targets = self.find_target()
        for building in targets:
            if (x == 0 and y == 0 and building.name == "TownCenter") or \
               (x == 0 and y == 1 and building.name == "Barracks") or \
               (x == 0 and y == 2 and building.name == "Archery") or \
               (x == 1 and y == 0 and building.name == "Stable"):
                target = building
                break

        if target is not None:
            # Get the position of the target to attack
            target_pos = target.pos
            co = -5  # Offset for target positioning based on unit types

            # Iterate through all AI units to launch attacks
            for unit in self.AI_unit:
                if unit.name == "Cavalier":
                    unit.set_target((target_pos[0] + co, target_pos[1]))  # Set target position for Cavalier
                    for x in range(unit.pos[0] - unit.range, unit.pos[0] + unit.range):
                        for y in range(unit.pos[1] - unit.range, unit.pos[1] + unit.range):
                            if self.map.units.get(x, {}).get(y):  # Check if unit exists at position
                                self.map.list_units_atk.append((unit, self.map.units[x][y]))  # Add attack pair
                                self.map.list_attacker_defender.append((unit, self.map.buildings.get(x, {}).get(y)))
                                co += 1
                elif unit.name == "Archer":
                    unit.set_target((target_pos[0], target_pos[1] + co))  # Set target position for Archer
                    for x in range(unit.pos[0] - unit.range, unit.pos[0] + unit.range):
                        for y in range(unit.pos[1] - unit.range, unit.pos[1] + unit.range):
                            if self.map.units.get(x, {}).get(y):  # Check if unit exists at position
                                self.map.list_units_atk.append((unit, self.map.units[x][y]))  # Add attack pair
                                co += 1

    def auto_defense(self):
        if self.all_in:
            return  # No need to defend if it's an all-in strategy

        # Move units to defense positions if health is low
        for soldier in self.AI_unit:
            if soldier.health <= 20:
                # Check various positions and try to move the unit to a safe location
                pos = soldier.pos
                if pos[0] <= 3 and pos[1] <= 3:
                    # Try to move the soldier to a nearby position if there's no collision
                    self._move_to_safe_position(soldier, pos, 1, 1)
                elif 3 < pos[0] <= 30 and pos[1] <= 3:
                    self._move_to_safe_position(soldier, pos, 1, 0)
                elif 30 < pos[0] <= 46 and pos[1] <= 3:
                    self._move_to_safe_position(soldier, pos, -1, 0)
                elif 30 < pos[0] <= 46 and 30 < pos[1] <= 46:
                    self._move_to_safe_position(soldier, pos, -1, -1)
                else:
                    self._move_to_safe_position(soldier, pos, 3, 3)  # Default safe position

    def _move_to_safe_position(self, soldier, current_pos, offset_x, offset_y):
        """Helper function to move soldier to a new position."""
        for dx in range(3):  # Try up to 3 different positions
            new_pos = (current_pos[0] + dx * offset_x, current_pos[1] + dx * offset_y)
            if not self.map.world.get(new_pos[0], {}).get(new_pos[1], {}).get("collision") and \
               self.map.units.get(new_pos[0], {}).get(new_pos[1]) is None:
                soldier.set_target(new_pos)
                break

    def find_target(self):
        """Find all targets on the map."""
        target_list = []
        for i in range(50):
            for j in range(50):
                building = self.map.buildings.get(i, {}).get(j)
                if building and building.team == "Blue":  # Only consider Blue team's buildings
                    target_list.append(building)
        return target_list

def create_villager(self, pos):
    """Create a villager near the TownCenter if possible and set their target."""
    if self.created_tc:
        for i in range(-1, 2):  # Check a 3x3 area around TownCenter
            for j in range(-1, 2):
                target_pos = (self.towncenter.pos[0] + i, self.towncenter.pos[1] + j)
                # Check if the position is not blocked by a collision
                if not self.map.world[target_pos[0]][target_pos[1]]["collision"]:
                    # Create a new Villager at the available position
                    new_villager = Villager(self.map.world[target_pos[0]][target_pos[1]], 
                                            self.map, self.resource_man, "Red", False)
                    self.AI_villager.append(new_villager)  # Add to the AI's villager list
                    new_villager.set_target(pos)  # Set the target position for the villager
                    return  # Stop after creating one villager

def check_villager(self):
    """Check if villagers are blocked and reassign tasks accordingly."""
    for villager in self.AI_villager:
        # Check if the villager's work position is not blocked (i.e., no collision)
        if not self.map.world[villager.pos[0] - 1][villager.pos[1]]["collision"]:
            villager.in_work = False  # Mark the villager as not working if blocked
    # Resource collection calls (for various resources)
    self.get_resource("Wood")  # Wood collection from trees
    self.get_resource("Gold")  # Gold collection
    self.get_resource("Food")  # Food collection
   

def create_Archer(self, x, y):
    """Create an Archer at the nearest Archery building and set their target."""
    for entity in self.map.entities:
        if entity.name == "Archery" and entity.team == "Red":
            archer = Archer(self.map.world[entity.pos[0]][entity.pos[1] + 1], 
                            self.map, self.map.resource_man, "Red", False)
            self.map.list_troop.append(archer)  # Add to the troop list
            self.AI_unit.append(archer)  # Add to the AI's unit list
            archer.set_target((x, y))  # Set target for the newly created Archer



def create_Cavalier(self, x, y):
    """Create a Cavalier at the nearest Stable and set their target."""
    for entity in self.map.entities:
        if entity.name == "Stable" and entity.team == "Red":
            cavalier = Cavalier(self.map.world[entity.pos[0]][entity.pos[1] + 1], 
                                self.map, self.map.resource_man, "Red", False)
            self.map.list_troop.append(cavalier)  # Add to the troop list
            self.AI_unit.append(cavalier)  # Add to the AI's unit list
            cavalier.set_target((x, y))  # Set target for the newly created Cavalier
