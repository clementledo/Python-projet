class Unit:
    def __init__(self, x, y, unit_type):
        self.x = x  # Position X de l'unité
        self.y = y  # Position Y de l'unité
        self.unit_type = unit_type  # Type d'unité (guerrier, archer)
        self.speed = 5
        self.destination = None
        self.health = 100  # Points de vie
        self.width = 32
        self.height = 32

    
    
    def update(self):
        """Met à jour l'unité, par exemple pour la faire se déplacer."""
        if self.destination:
            self.move_towards(self.destination) 
    
    def is_clicked(self, mouse_pos):
        """Vérifie si l'unité est cliquée selon la position de la souris"""
        mouse_x, mouse_y = mouse_pos
        # Vérifie si la souris est dans les limites de l'unité
        if self.x <= mouse_x <= self.x + self.width and self.y <= mouse_y <= self.y + self.height:
            return True
        return False
    
    def select_unit(self, mouse_pos):
        """Sélectionne l'unité si elle est cliquée."""
        for unit in self.model['units']:
            if unit.is_clicked(mouse_pos):
                self.selected_unit = unit
                break


    def move_towards(self, destination):
        """Déplace l'unité vers une destination."""
        dest_x, dest_y = destination
        if self.x < dest_x:
            self.x += min(self.speed, dest_x - self.x)
        elif self.x > dest_x:
            self.x -= min(self.speed, self.x - dest_x)

        if self.y < dest_y:
            self.y += min(self.speed, dest_y - self.y)
        elif self.y > dest_y:
            self.y -= min(self.speed, self.y - dest_y)

        # Si l'unité a atteint la destination, on arrête le mouvement
        if self.x == dest_x and self.y == dest_y:
            self.destination = None        

    def move(self, new_x, new_y):
        self.x = new_x
        self.y = new_y

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.die()

    def die(self):
        print(f"L'unité {self.unit_type} est morte.")


class Villager(Unit):
    def __init__(self, x, y):
        super().__init__(x, y, "villageois")
        self.hp = 25  # Points de vie
        self.attack = 2  # Points d'attaque
        self.speed = 0.8  # Vitesse de déplacement (tuiles/seconde)
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