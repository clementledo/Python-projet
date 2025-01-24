from models.Buildings.building import Building
from ..units.archer import Archer

class Archery_Range(Building) :
    def __init__(self,pos) :
        super().__init__("Archery_range",50,500,(3,3),'A',pos)
        self.cost["wood"] = 175
        
    def spawn_archer(self) :
        self.remove_ressources(self,25,'W')
        self.remove_ressources(self,45,'G')
        return Archer(25,45,30,30,1,'a',4)
    """(cost1,cost2,training_time,hp,speed,symbol,attack,pos)"""