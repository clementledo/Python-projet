from models.Buildings.building import Building
from ..units.villager import Villager
from ..Resources import Ressource

"""peut faire spawn des villageois"""       
class Town_center(Building) :
    """pour chaque type d'unitÃ©s, de ressources et de bÃ¢timents, avoir un attribut statique liste ? non, une liste pour chaque classe mÃ¨re batiment et unit"""
    
    def __init__(self, pos) :
        #self.population_max = self.population_max +5
        super().__init__(350, 150, 1000, (4,4), 'T', pos)
        self.size=(4,4)

    def add_ressources(type_ressource) :
        """reprendre le diagramme uml tile pour complÃ©ter le constructeur"""
        return Ressource(type_ressource)

    def remove_ressources (self,number,type) : 
        return

    def spawn_v(self) : 
        self.remove_ressources(self,50,'F')
        return Villager(50,25,25,1,'v',2)
    """(cost1,cost2,training_time,hp,speed,symbol,attack,pos)"""