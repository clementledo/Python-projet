from models.Buildings.building import Building
from ..units.swordsman import Swordsman

class Barrack(Building) :
    
    def __init__(self,pos) :
        super().__init__("Barracks",175,50,500,3,'B',pos,'new')
        
    def spawn_swordsman(self):
        self.remove_ressources(self,50,'F')
        self.remove_ressources(self,20,'G')
        return Swordsman(50,20,20,40,0.9,'s',4)
    """(cost1,cost2,training_time,hp,speed,symbol,attack,pos)"""