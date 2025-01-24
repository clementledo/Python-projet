from models.Buildings.building import Building

class Keep(Building) :
    def __init__(self,pos) :
        super().__init__(self,80,800,1,'K',pos)
        self.cost["wood"] = 35
        self.cost["gold"] = 125
        self.attack = 5
        self.range = 8
    
    def fire_arrows(self,unit) :
        unit.take_damage(self.attack)