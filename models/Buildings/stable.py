from models.Buildings.building import Building
from ..units.horseman import Horseman

class Stable(Building) :
    
    def __init__(self,pos) :
        super().__init__(self,175,50,500,3,'S',pos,'new')
        
    def spawn_horseman(self) :
        self.remove_ressources(self,80,'F')
        self.remove_ressources(self,20,'G')
        return Horseman(80,20,30,45,1.2,'h',4)
    """(cost1,cost2,training_time,hp,speed,symbol,attack,pos)"""