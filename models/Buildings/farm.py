from models.Buildings.building import Building

"""ProblÃ¨me pour le contenant"""
class Farm(Building) :
    
    cont = 300
    
    def __init__(self,pos) :
        super().__init__(self, 60, 10, 100, 2, 'F', pos, 'new')