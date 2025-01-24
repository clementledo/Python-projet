from models.Buildings.building import Building

"""ProblÃ¨me pour le contenant"""
class Farm(Building) :
    def __init__(self,pos) :
        super().__init__("Farm", 10, 100, (1,1), 'F', pos)
        self.cost["wood"] = 60