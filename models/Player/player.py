class Player:
        
    def __init__(self,name):
        self.name = name
        self.resources = {}
        self.population_current: int = 0
        self.population_max = 200
        self.units = []
        self.buildings = []
        
    def add_unit(self, unit):
        if self.population_current + 1 > self.population_max:
            raise ValueError(f"Cannot add unit: population limit exceeded.")
        self.units.append(unit)
        self.population_current += 1
        
    def remove_unit(self,unit):
        if unit in self.units:
            self.units.remove(unit)
            self.population_current -= 1
            
    def update_resources(self,resource,amount):
        if resource not in self.resources:
            self.resources[resource] = 0
        if self.resources[resource] + amount < 0:
            raise ValueError(f"Insufficient {resource.__name__} resources.")
        self.resources[resource] += amount
        
    def can_afford(self,cost):
        for resource, amount in cost.items():
            if self.resources.get(resource, 0) < amount:
                return False
        return True