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
