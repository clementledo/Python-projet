from models.Buildings.building import Building

class Keep(Building) :
    
    gold_cost=125 
    range=8
    attack=5
    
    def __init__(self,pos) :
        super().__init__(name = "Keep",construction_time=80, hp=800,size= (1,1), symbol='K',pos=pos)
    
    def fire_arrows(self,unit) :
        unit.gethp() = unit.gethp() - self.attack