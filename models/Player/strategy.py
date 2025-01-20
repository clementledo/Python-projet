from units.unit import Unit 
from units.villager import Villager
from Buildings.town_center import Town_center
from models.map import Map

from units.unit import unitStatus
from building.town_hall import TownHall
from resource.tile import Type  
class Strategy:
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
        for town_hall in self.ai_controller.buildings_by_type("TownHall"):
            if self.ai_controller.resources["Food"] >= 50 and not town_hall.is_training:
                town_hall.train_unit("Villager")

        # Assign Villagers to gather Food and Wood
        for villager in self.ai_controller.units_by_type("Villager"):
            if villager.task is None:
                if self.ai_controller.resources["Food"] < 300:
                    villager.collect_resource("Food")
                else:
                    villager.collect_resource("Wood")

        # Build Houses if population cap is reached
        if self.ai_controller.population >= self.ai_controller.population_cap:
            self.ai_controller.build_building_near("House", self.ai_controller.town_hall_position())

        # Build Farms in advance
        if self.ai_controller.count_buildings_by_type("Farm") < 6:
            self.ai_controller.build_building_near("Farm", self.ai_controller.town_hall_position())

        # Build additional Town Halls up to 4
        if self.ai_controller.count_buildings_by_type("TownHall") < 4:
            if self.ai_controller.resources["Wood"] >= 350:
                position = self.ai_controller.find_nearby_available_position(
                    *self.ai_controller.town_hall_position(), (4, 4))
                self.ai_controller.build_building("TownHall", position)

    def execute_second_phase(self):
        """
        Executes the second phase of the game.
        Priority:
        - Continue generating Villagers until 100
        - Transition Villagers to Gold collection gradually
        - Build Camps near resource nodes
        - Train a balanced army
        - Build Farms in advance to ensure food availability
        """
        # Generate Villagers until 100
        for town_hall in self.ai_controller.buildings_by_type("TownHall"):
            if (self.ai_controller.unit_count("Villager") < 100 and
                    self.ai_controller.resources["Food"] >= 50 and not town_hall.is_training):
                town_hall.train_unit("Villager")

        # Gradually transition Villagers to collect Gold
        gold_villagers = self.ai_controller.count_villagers_collecting("Gold")
        if gold_villagers < self.ai_controller.unit_count("Villager") * 0.3:  # Target 30% collecting Gold
            for villager in self.ai_controller.units_by_type("Villager"):
                if villager.task == "collecting Wood":
                    villager.collect_resource("Gold")

        # Build Camps near resource nodes
        for resource_type in ["Wood", "Gold"]:
            for node in self.ai_controller.resource_nodes(resource_type):
                if self.ai_controller.should_build_camp(node):
                    self.ai_controller.build_building_near("Camp", node.position)

        # Train a balanced army
        if self.ai_controller.resources["Food"] >= 50 and self.ai_controller.resources["Gold"] >= 20:
            for building_type in ["Barracks", "Stable", "Archery_Range"]:
                for building in self.ai_controller.buildings_by_type(building_type):
                    if not building.is_training:
                        building.train_unit(self.ai_controller.next_unit_type(building_type))

        # Build Farms in advance
        if self.ai_controller.count_buildings_by_type("Farm") < 10:
            self.ai_controller.build_building_near("Farm", self.ai_controller.town_hall_position())

    def execute(self):
        if self.phase == 1:
            self.execute_begin_phase()
            if self.ai_controller.count_buildings_by_type("TownHall") >= 4:
                self.phase = 2
        elif self.phase == 2:
            self.execute_second_phase()