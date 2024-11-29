from models.Buildings.building import Building

class Keep(Building) :
    
    gold_cost=125 
    range=8
    attack=5
    
    def __init__(self,pos) :
        super().__init__(self,35,80,800,1,'K',pos,'new')
    
    def fire_arrows(self,unit) :
        unit.gethp() = unit.gethp() - self.attack