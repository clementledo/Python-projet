from models.units.villager import Villager
from models.Buildings.town_center import Town_center
from models.map import Map
from models.units.unit import Unit
from models.units.unit import unitStatus
from models.Resources.Tile import *
import random

class Strategy:
    AGGRESSIVE = "aggressive"
    DEFENSIVE = "defensive"
    ECONOMIC = "economic"
    
    def __init__(self, ai_controller):
        self.ai_controller = ai_controller
        self.phase = 1
        


    def execute_begin_phase(self):
        """
        Executes the beginning phase of the game.
        Priority:
        - Generate Villagers
        - Gather Food and Wood
        - Build Houses and Farms
        - Construct Town Halls up to 4
        """
        # Generate Villagers
        for Town_center in self.ai_controller.buildings_by_type("Town_center"):
            if self.ai_controller.resources["Food"] >= 50 and not Town_center.is_training:
                Town_center.train_unit("Villager")

        # Assign Villagers to gather Food and Wood
        for villager in self.ai_controller.units_by_type("Villager"):
            if villager.task is None:
                if self.ai_controller.resources["Food"] < 300:
                    villager.collect_resource("Food")
                else:
                    villager.collect_resource("Wood")

        # Build Houses if population cap is reached
        if self.ai_controller.population >= self.ai_controller.population_cap:
            self.ai_controller.build_building_near("House", self.ai_controller.Town_center_position())

        # Build Farms in advance
        if self.ai_controller.count_buildings_by_type("Farm") < 6:
            self.ai_controller.build_building_near("Farm", self.ai_controller.Town_center_position())

        # Build additional Town Halls up to 4
        if self.ai_controller.count_buildings_by_type("Town_center") < 4:
            if self.ai_controller.resources["Wood"] >= 350:
                position = self.ai_controller.find_nearby_available_position(
                    *self.ai_controller.town_hall_position(), (4, 4))
                self.ai_controller.build_building("Town_center", position)

    
    def execute(self):
        if self.phase == 1:
            self.execute_begin_phase()
            if self.ai_controller.count_buildings_by_type("Town_center") >= 4:
                self.phase = 2
        elif self.phase == 2:
            self.execute_second_phase()

    def execute_attack_phase(self):
        # Collect military units
        military_units = []
        for unit_type in ["Archer", "Swordman", "Horseman","Villager"]:
            military_units.extend(self.ai_controller.units.get(unit_type, []))
        
        # Find enemy units
        enemy_units = [
            u for u in self.ai_controller.game_state.model['units'] 
            if u.player_id != self.ai_controller.player_id
        ]
        
        # Attack if enough military units and enemies exist
        if len(military_units) >= len(enemy_units):
            # Find a target
            target = self.ai_controller.find_nearby_targets(military_units[0], enemy_units)
            if target:
                print(f"Found Target at {target.position}")
                position_attack = (target.position[0] + 1, target.position[1]) 
                for unit in military_units:
                   unit.move_toward(position_attack, self.ai_controller.game_state.carte)
                   if self.ai_controller.get_distance(position_attack,unit.position)==0:
                       unit.atk(target)
    def die(self, game_state):                  
        units_to_remove = [unit for unit in self.ai_controller.units if unit.health <= 0]
        for dead_unit in units_to_remove:
            self.models.units.remove(dead_unit)  # Remove from model
            game_state.remove_unit(dead_unit)    # Remove from game state
            
            # Update player stats if needed
            if hasattr(dead_unit, 'player_id'):
                if dead_unit.player_id in game_state.players:
                    game_state.players[dead_unit.player_id].update_unit_count()