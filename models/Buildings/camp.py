from models.Buildings.building import Building
from ..Resources import Ressource

"""ProblÃ¨me pour le contenant"""
class Camp(Building) : 
    
    cont = 0
    
    def __init__(self,pos) :
        super().__init__(self,100,25,200,2,'C',pos,'new')
        
    def add_ressources(type_ressource) :
        """reprendre le diagramme uml tile pour complÃ©ter le constructeur"""
        return Ressource(type_ressource)
    
    def remove_ressources (self,number,type) : 
        return