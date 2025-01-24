from models.Buildings.building import Building

"""ProblÃ¨me pour le contenant"""
class Farm(Building) :
    
    cont = 300
    
    def __init__(self,pos) :
        super().__init__(name = "Farm", construction_time=10, hp=100,size= (2,2), symbol='F',pos=pos)