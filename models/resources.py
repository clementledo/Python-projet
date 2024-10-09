class Resource:
    def __init__(self):
        self.starting_resources = {
            "Wood": STARTING_RESOURCES[0],
            "Gold": STARTING_RESOURCES[1],
            "Food": STARTING_RESOURCES[2]
        }

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
            1: wood_icon,
            2: gold_icon,
            3: food_icon
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
