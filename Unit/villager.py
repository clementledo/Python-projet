
from unit.unit import Unit

class Villager(Unit):
    def __init__(self, x, y,map):
        super().__init__(x, y, "villager", 2, 0.8, 25, map)
        self.resource_capacity = 20  # Peut transporter 20 ressources
        self.resource_gather_rate = 25 / 60  # 25 ressources par minute (en secondes)
        self.is_building = False  # Indique si le villageois est en train de construire
        self.training_time = 25  # Temps d'entraînement en secondes
    
    def start_building(self, building, builders_count):
        """Démarre la construction d'un bâtiment."""
        self.is_building = True
        self.building = building
        nominal_time = building.nominal_construction_time
        self.remaining_construction_time = (3 * nominal_time) / (builders_count + 2)
        print(f"Construction commencée. Temps de construction réel : {self.remaining_construction_time} secondes.")
    
    def update_building(self, delta_time):
        """Met à jour la construction en cours."""
        if self.is_building:
            self.remaining_construction_time -= delta_time
            if self.remaining_construction_time <= 0:
                print(f"Construction terminée du bâtiment : {self.building.name}")
                self.is_building = False

    def gather_resources(self, resource_type, delta_time):
        """Simule la collecte de ressources. Collecte au rythme de 25/minute."""
        resources_gathered = self.resource_gather_rate * delta_time
        if resources_gathered > self.resource_capacity:
            resources_gathered = self.resource_capacity
        print(f"{resources_gathered} unités de {resource_type} collectées.")
    
    def update(self):
        """Met à jour le villageois (construction, collecte, etc.)."""
        delta_time = 1 / 60  # Exemple de 60 FPS pour gérer le temps
        if self.is_building:
            self.update_building(delta_time)
        # Autres actions possibles (comme la collecte de ressources
