from .unit import Unit # type: ignore
from .unit import unitStatus

class Villager(Unit):
    def __init__(self, x, y, map):
        super().__init__(x, y, "Villager", 2, 1.0, 25, map)
        self.is_gathering = False
        self.gathering_progress = 0
        self.gathering_speed = 1
        self.carry_capacity = 10
        self.carried_resources = 0
        self.resource_type = None
        self.nearest_dropoff = None
        self.resource_capacity = 20  # Peut transporter 20 ressources
        self.resource_gather_rate = 25 / 60  # 25 ressources par minute (en secondes)
        self.training_time = 25  # Temps d'entraînement en secondes

        self.current_resources = 0
        self.current_resource_type = None
        self.building = None
        self.remaining_construction_time = 0
        self.attack_range = 1
    
    def start_building(self, building, builders_count):
        """Démarre la construction d'un bâtiment."""
        self.status = unitStatus.BUILDING
        self.building = building
        nominal_time = building.nominal_construction_time
        self.remaining_construction_time = (3 * nominal_time) / (builders_count + 2)
        print(f"Construction commencée. Temps de construction réel : {self.remaining_construction_time} secondes.")
    
    def update_building(self, delta_time):
        """Met à jour la construction en cours."""
        if self.status == unitStatus.BUILDING:
            self.remaining_construction_time -= delta_time
            if self.remaining_construction_time <= 0:
                print(f"Construction terminée du bâtiment : {self.building.name}")
                self.status = unitStatus.IDLE
                self.building = None

    def start_gathering(self, resource_type):
        """Commence la collecte d'un type de ressource."""
        self.status = unitStatus.GATHERING
        self.current_resource_type = resource_type
        print(f"Début de la collecte de {resource_type}")

    def gather_resources(self, resource_type, delta_time):
        """Simule la collecte de ressources. Collecte au rythme de 25/minute."""
        resources_gathered = self.resource_gather_rate * delta_time
        if resources_gathered > self.resource_capacity:
            resources_gathered = self.resource_capacity
        print(f"{resources_gathered} unités de {resource_type} collectées.")
    
    def gather(self, resource_pos):
        tile = self.grid.get_tile(resource_pos[0], resource_pos[1])
        if tile.resource:
            self.resource_type = self.get_resource_type(tile.resource)
            self.status = unitStatus.GATHERING
            self.is_gathering = True
            self.destination = resource_pos

    def get_resource_type(self, resource):
        """Map resource to resource type"""
        resource_mapping = {
            "W": "wood",
            "F": "food",
            "G": "gold"
        }
        return resource_mapping.get(resource.symbol, "food")

    def update_gathering(self):
        """Update gathering progress"""
        if self.status == unitStatus.GATHERING:
            if self.carried_resources >= self.carry_capacity:
                self.return_resources()
            else:
                tile = self.grid.get_tile(self.position[0], self.position[1])
                if tile.resource:
                    self.gathering_progress += self.gathering_speed
                    if self.gathering_progress >= 100:
                        self.carried_resources += 1
                        self.gathering_progress = 0

    def update(self):
        """Met à jour le villageois (construction, collecte, etc.)."""
        delta_time = 1 / 60  # Exemple de 60 FPS pour gérer le temps
        
        if self.status == unitStatus.BUILDING:
            self.update_building(delta_time)
        elif self.status == unitStatus.GATHERING:
            self.gather_resources(self.current_resource_type, delta_time)
