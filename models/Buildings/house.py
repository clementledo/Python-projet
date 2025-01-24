from models.Buildings.building import Building

class House(Building) :
    def __init__(self, pos) :
        # self.population_max = self.population_max +5
        super().__init__(name = "House",construction_time=25, hp=200,size= (2,2), symbol='H',pos=pos)
