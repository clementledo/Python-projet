from models.Buildings.building import Building
from ..units.swordsman import Swordsman

class Barrack(Building) :
    
    def __init__(self,pos) :
        super().__init__("Barracks",20,500,(3,3),'B',pos)
        self.cost["wood"] = 175
        self.training_time = 0
        self.training_cooldown = 20
        self.unit_cost = {"food": 50, "gold": 20}
        self.unit = None
        self.unit_type = "Swordsman"
        
    def train_unit(self, pos, game_state):
        self.unit = Swordsman(pos[0], pos[1], game_state.carte)
        self.unit.player_id = self.player_id
        self.training_time = self.training_cooldown
    """(cost1,cost2,training_time,hp,speed,symbol,attack,pos)"""
    
    def is_idle(self):
        return super().is_idle() and self.training_time <= 0
    
    def check_training(self, game_state):
        self.update()
        #print(f"Training time: {self.training_time}")
        if self.training_time <= 1e-2 and self.unit:
            self.training_time = 0
            print("Swordman training complete!")
            game_state.model['units'].append(self.unit)
            return self.unit  
        return None     
    
    def update(self):
        """Update training cooldown"""
        if self.training_time > 0:
            self.training_time -= 1*1/60