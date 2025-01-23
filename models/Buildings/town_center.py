from models.Buildings.building import Building
from ..units.villager import Villager
from ..Resources import Ressource

class Town_center(Building):
    def __init__(self, pos,use_terminal_view=False):
        super().__init__("Town_center", 10, 1000, (4, 4), 'T', pos)
        self.cost["Wood"] = 350
        self.training_time = 0
        self.training_cooldown = 50
        self.villager_cost = {"food": 50}
        self.spawn_offset = (4, 2)
        self.player_id=1  # Spawn position relative to TC

    def train_villager(self, game_state):
        """Train a new villager if resources available"""
        player_resources = game_state.player_resources[self.player_id]
        
        if (self.training_time <= 0 and 
            player_resources["food"] >= self.villager_cost["food"]):
            
            # Create new villager
            spawn_x = self.pos[0] + self.spawn_offset[0]
            spawn_y = self.pos[1] + self.spawn_offset[1]
            new_villager = Villager(spawn_x, spawn_y, game_state.carte)
            new_villager.player_id = self.player_id
            
            # Deduct resources
            game_state.player_resources[self.player_id]["food"] -= self.villager_cost["food"]
            
            # Add to game
            game_state.model['units'].append(new_villager)
            self.training_time = self.training_cooldown
            return True
        return False

    def update(self):
        """Update training cooldown"""
        if self.training_time > 0:
            self.training_time -= 1
