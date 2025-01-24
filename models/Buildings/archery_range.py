from models.Buildings.building import Building
from ..units.archer import Archer

class Archery_Range(Building) :
    range = 4
    def __init__(self,pos) :
        super().__init__(name = "Archery_range",construction_time=50, hp=500,size= (3,3), symbol='A',pos=pos)

        
    def spawn_archer(self) :
        self.remove_ressources(self,25,'W')
        self.remove_ressources(self,45,'G')
        return Archer(25,45,30,30,1,'a',4)
    """(cost1,cost2,training_time,hp,speed,symbol,attack,pos)"""