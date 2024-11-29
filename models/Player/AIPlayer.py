from player import Player
from gameStrategy import GameStrategy

class IAPlayer(Player):
    
    def __init__(self,name,strategy):
        super().__init__(name)
        self.strategy = strategy
        self.knowledge_base = None
        self.build_order = []
        
    def decide_action(self):
        """
        Décide l'action à prendre en fonction de la stratégie et de l'état du jeu.
        """
        if self.strategy == GameStrategy.AGGRESSIVE:
            return self.aggressive_strategy()
        elif self.strategy == GameStrategy.DEFENSIVE:
            return self.defensive_strategy()
        elif self.strategy == GameStrategy.ECONOMIC:
            return self.economic_strategy()
        elif self.strategy == GameStrategy.BALANCED:
            return self.balanced_strategy()
        
        
    def aggressive_strategy(self):
        """Logique pour une stratégie agressive."""
        # Priorité : recruter des unités d'attaque si possible
        if self.resources["food"] >= 50 and self.resources["gold"] >= 20:
            return "train_swordsman"
        elif len(self.units) > 5:
            return "attack"
        return "gather_resources" # 

    def defensive_strategy(self, buildings):
        """Logique pour une stratégie défensive."""
        # Priorité : construire des structures défensives
        if self.resources["wood"] >= 35 and self.resources["gold"] >= 125:
            return "build_keep"
        elif len(self.units) < len(buildings) * 2:
            return "train_villager"
        return "gather_resources"

    def economic_strategy(self):
        """Logique pour une stratégie économique."""
        # Priorité : construire des bâtiments économiques et récolter des ressources
        if self.resources["wood"] >= 60 : # and "farm" not in [b["type"] for b in buildings]
            return "build_farm"
        elif self.resources["food"] < 100 or self.resources["wood"] < 100 or self.resources["gold"] < 100:
            return "gather_resources"
        elif len(self.units) < 10:
            return "train_villager"
        return "expand"

    def balanced_strategy(self):
        """Logique pour une stratégie équilibrée."""
        # Mélange entre attaque, défense et économie
        if len(self.units) < 10:
            return self.economic_strategy()
        elif len(self.units) > 15:
            return self.aggressive_strategy()
        else:
            return self.defensive_strategy()
    