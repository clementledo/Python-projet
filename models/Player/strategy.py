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
    
    def __init__(self, ai_controller, strategy_type):
        self.ai_controller = ai_controller
        self.strategy_type = strategy_type
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