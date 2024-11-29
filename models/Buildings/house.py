from models.Buildings.building import Building

class House(Building) :
    def __init__(self, pos) :
        self.population_max = self.population_max +5
        super().__init__(self, 25, 25, 200, 3, 'H', pos, 'new')