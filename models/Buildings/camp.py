from models.Buildings.building import Building
from ..Resources import Ressource

"""ProblÃ¨me pour le contenant"""
class Camp(Building) : 
    
    cont = 0
    
    def __init__(self,pos) :
        super().__init__(name = "castel",construction_time=25, hp=200,size= (2,2), symbol='C',pos=pos)
        
    def add_ressources(type_ressource) :
        """reprendre le diagramme uml tile pour complÃ©ter le constructeur"""
        return Ressource(type_ressource)
    
    def remove_ressources (self,number,type) : 
        return