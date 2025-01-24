from models.Buildings.building import Building
from models.units.unit import unitStatus  # Import unitStatus
from models.Buildings.town_center import Town_center
from enum import Enum
from models.units.villager import Villager
from models.units.archer import Archer
from models.units.horseman import Horseman
from models.Buildings.barrack import Barrack

class Strategy(Enum):
    AGGRESSIVE = "aggressive"
    DEFENSIVE = "defensive"
    ECONOMIC = "economic"

class IAPlayer:
    def __init__(self, player_id, game_state, strategy=Strategy.AGGRESSIVE):
        self.player_id = player_id
        self.game_state = game_state
        self.strategy = strategy
        self.units = []
        self.buildings = []
        self.resources = game_state.player_resources[player_id]
        
        # Strategy parameters
        if strategy == Strategy.AGGRESSIVE:
            self.min_villagers = 3
            self.min_warriors = 8
            self.attack_threshold = 5
        elif strategy == Strategy.DEFENSIVE:
            self.min_villagers = 5
            self.min_warriors = 4
            self.attack_threshold = 8
        else:  # ECONOMIC
            self.min_villagers = 8
            self.min_warriors = 2
            self.attack_threshold = 10

    def update(self):
        # Update unit lists
        self.units = [u for u in self.game_state.model['units'] if u.player_id == self.player_id]
        self.buildings = [b for b in self.game_state.model['buildings'] if b.player_id == self.player_id]
        
        if self.strategy == Strategy.AGGRESSIVE:
            self.execute_aggressive_strategy()
        elif self.strategy == Strategy.DEFENSIVE:
            self.execute_defensive_strategy()
        else:
            self.execute_economic_strategy()

    def execute_aggressive_strategy(self):
        military = [u for u in self.units if u.unit_type in ["Archer", "Horseman"]]
        
        # Priorité: Construction d'unités militaires
        if len(military) < self.min_warriors:
            self.train_military_unit()
        #else:
            #self.attack_enemy()

    def execute_defensive_strategy(self):
        # Priorité: Défense de la base et économie
        if not self.is_base_secure():
            self.defend_base()
        else:
            self.gather_resources()

    def execute_economic_strategy(self):
        # Priorité: Collecte de ressources et expansion
        villagers = [u for u in self.units if u.unit_type == "Villager"]
        if len(villagers) < self.min_villagers:
            self.train_villager()
        self.gather_resources()
        
    def is_base_secure(self):
        # Vérifie si la base est menacée
        enemy_units = [u for u in self.game_state.model['units'] if u.player_id != self.player_id]
        base = self.get_main_base()
        if base:
            nearby_enemies = [u for u in enemy_units if self.get_distance(u.position, base.pos) < 10]
            return len(nearby_enemies) == 0
        return False

    def defend_base(self):
        military = [u for u in self.units if u.unit_type in ["Archer", "Horseman"]]
        base = self.get_main_base()
        if base:
            for unit in military:
                unit.move_to((base.pos[0] + 2, base.pos[1] + 2))

    def attack_enemy(self):
        military = [u for u in self.units if u.unit_type in ["Archer", "Horseman"]]
        enemy_units = [u for u in self.game_state.model['units'] if u.player_id != self.player_id]
        
        if len(military) >= self.attack_threshold and enemy_units:
            target = self.find_best_target(enemy_units)
            for unit in military:
                unit.move_toward(target.position,self.game_state.carte)

    def find_best_target(self, enemy_units):
        # Prioritize villagers and weak units
        villagers = [u for u in enemy_units if u.unit_type == "Villager"]
        return villagers[0] if villagers else enemy_units[0]

    def get_main_base(self):
        town_centers = [b for b in self.buildings if b.__class__.__name__ == "Town_center"]
        return town_centers[0] if town_centers else None

    def train_military_unit(self):
        """Create military unit if possible"""
        barracks = [b for b in self.buildings if isinstance(b, Barrack)]
        if barracks and self.resources['food'] >= 50:
            self.resources['food'] -= 50
            new_pos = (barracks[0].pos[0] + 1, barracks[0].pos[1] + 1)
            new_unit = Horseman(new_pos[0], new_pos[1], self.game_state.carte)
            new_unit.player_id = self.player_id
            self.game_state.model['units'].append(new_unit)

        """ elif self.resources['wood'] >= 175:
            self.construct_building(Barrack(), (0,0)) """
        

    def train_villager(self):
        """Create villager if possible"""
        town_centers = [b for b in self.buildings if isinstance(b, Town_center)]
        if town_centers and self.resources['food'] >= 50:
            self.resources['food'] -= 50
            new_pos = (town_centers[0].pos[0] + 1, town_centers[0].pos[1] + 1)
            new_unit = Villager(new_pos[0], new_pos[1], self.game_state.carte)
            new_unit.player_id = self.player_id
            self.game_state.model['units'].append(new_unit)

    def gather_resources(self):
        """Make villagers gather resources"""
        villagers = [u for u in self.units if isinstance(u, Villager)]
        for villager in villagers:
            if villager.status == unitStatus.IDLE:
                resources = self.game_state.carte.get_resources()
                if resources:
                    closest = min(resources, key=lambda r: 
                        abs(r[0] - villager.position[0]) + abs(r[1] - villager.position[1]))
                    villager.move_to(closest)

    def get_distance(self, pos1, pos2):
        """Calculate Manhattan distance between two positions"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
