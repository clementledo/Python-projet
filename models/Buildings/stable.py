from models.Buildings.building import Building
from ..units.horseman import Horseman

class Stable(Building) :
    
    def __init__(self,pos) :
        super().__init__(name = "Stable",construction_time=50, hp=500,size= (3,3), symbol='S',pos=pos)
        
    def spawn_horseman(self) :
        self.remove_ressources(self,80,'F')
        self.remove_ressources(self,20,'G')
        return Horseman(80,20,30,45,1.2,'h',4)
    """(cost1,cost2,training_time,hp,speed,symbol,attack,pos)"""