from models.Buildings.building import Building
from ..Resources import Ressource

"""ProblÃ¨me pour le contenant"""
class Camp(Building) : 
    def __init__(self,pos) :
        super().__init__("Camp",25,200,(2,2),'C',pos)
        self.cost["wood"] = 100
        
    def add_ressources(type_ressource) :
        """reprendre le diagramme uml tile pour complÃ©ter le constructeur"""
        return Ressource(type_ressource)
    
    def remove_ressources (self,number,type) : 
        return