import pygame
class Resource:
    def __init__(self,STARTING_RESOURCES):
        self.starting_resources = {
            "Wood": STARTING_RESOURCES[0],
            "Gold": STARTING_RESOURCES[1],
            "Food": STARTING_RESOURCES[2]
        }

        
        self.costs = {
            "TownCenter": {"Wood": 350, "Gold": 0, "Food": 0},
            "Barracks": {"Wood": 175, "Gold": 0, "Food": 0},
            "House": {"Wood": 25, "Gold": 0, "Food": 0},
            "Archery": {"Wood": 175, "Gold": 0, "Food": 0},
            "Stable": {"Wood": 175, "Gold": 0, "Food": 0},
            "Farm": {"Wood": 60, "Gold": 0, "Food": 0},
            "Camp": {"Wood": 100, "Gold": 0, "Food": 0},
            "Keep": {"Wood": 35, "Gold": 125, "Food": 0},
            "Villager": {"Wood": 0, "Gold": 0, "Food": 50},
            "Swordsman": {"Wood": 0, "Gold": 20, "Food": 50},
            "Horseman": {"Wood": 0, "Gold": 20, "Food": 80},
            "Archer": {"Wood": 25, "Gold": 45, "Food": 0}
        }

        self.icons = {
            1: pygame.image.load("assets/iconfood.png"),
            2: pygame.image.load("assets/icongold.png"),
            3: pygame.image.load("assets/iconfood.png")
        }

    """ I define 2 teams Blue and Red """ 
    def is_affordable(self, ent):
        affordable = True
        for resource, cost in self.costs[ent].items():
            if cost > self.starting_resources[resource]:
                affordable = False
        return affordable

    def buy(self, ent):
        achat = ent.name
        if ent.team == "Blue":
            for resource, cost in self.costs[achat].items():
                if self.starting_resources[resource] >= cost:
                    self.starting_resources[resource] -= cost
                else:
                    return -1
        elif ent.team == "Red":
            for resource, cost in self.costs[achat].items():
                if self.starting_resources_AI[resource] >= cost:
                    self.starting_resources_AI[resource] -= cost
                else:
                    return -1

    def buy_age(self, ent):

        achat = ent.age

        if ent.team == "Blue":
            for resource, cost in self.costs[achat].items():
                if self.starting_resources[resource] >= cost:
                    self.starting_resources[resource] -= cost
                else:
                    return -1
        elif ent.team == "Red":
            for resource, cost in self.costs[achat].items():
                if self.starting_resources_AI[resource] >= cost:
                    self.starting_resources_AI[resource] -= cost
                else:
                    return -1

    def get_type(self) -> Type:
        return self.type

    def get_quantity(self) -> int:
        return self.quantity

    def __repr__(self):
        return f"Resource(type={self.type}, symbol='{self.symbol}', quantity={self.quantity}

class Wood(Resource):
    def __init__(self):
        super().__init__(Type.Wood, 1 , 100)

class Food(Resource):
    def __init__(self, farm: str = None):
        super().__init__(Type.Food, 2 , 300)
        self.farm = farm
        
    def __repr__(self):
        base_repr = super().__repr__()
        
class Gold(Resource):
    def __init__(self):
        super().__init__(Type.Gold, 3 , 800)
