from .unit import Unit
from .unit import unitStatus
import pygame
import os

class Villager(Unit):
    def __init__(self, x, y, map):
        super().__init__(x, y, "Villager", 0.5, 1.0, 25, map)
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

        # Animation attributes
        self.walking_sprites = []
        self.standing_sprites = []
        self.current_frame = 0
        self.animation_speed = 0.6  # Seconds per frame
        self.last_update = pygame.time.get_ticks()
        self.load_walking_sprites()
        self.load_standing_sprites()
    
    def load_walking_sprites(self):
        """Load all walking animation sprites"""
        sprite_dir = "assets/Sprites/Villager/Walk"
        for i in range(16, 76):  # 75 frames
            sprite_path = os.path.join(sprite_dir, f"Villagerwalk{i:03d}.png")
            try:
                sprite = pygame.image.load(sprite_path).convert_alpha()
                self.walking_sprites.append(sprite)
            except pygame.error as e:
                print(f"Couldn't load sprite: {sprite_path}")
                print(e)

    def load_standing_sprites(self):
        """Load all standing animation sprites"""
        sprite_dir = "assets/Sprites/Villager/Stand"
        for i in range(53, 75):  # Adjust range based on actual sprite count
            sprite_path = os.path.join(sprite_dir, f"Villagerstand{i:03d}.png")
            try:
                sprite = pygame.image.load(sprite_path).convert_alpha()
                self.standing_sprites.append(sprite)
            except pygame.error as e:
                print(f"Couldn't load sprite: {sprite_path}")
                print(e)
    
    def get_current_sprite(self):
        """Returns the current sprite based on unit state"""
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_speed * 1000:
            self.last_update = now
            if self.status == unitStatus.MOVING:
                self.current_frame = (self.current_frame + 1) % len(self.walking_sprites)
                return self.walking_sprites[self.current_frame]
            else:
                self.current_frame = (self.current_frame + 1) % len(self.standing_sprites)
                return self.standing_sprites[self.current_frame]
        
        # Return current frame without updating
        if self.status == unitStatus.MOVING:
            return self.walking_sprites[self.current_frame]
        return self.standing_sprites[self.current_frame]

    def move_towards(self, position, grid):
        """Handle movement and animation"""
        result = super().move_towards(position, grid)
        if result and self.status == unitStatus.MOVING:
            now = pygame.time.get_ticks()
            if now - self.last_update > self.animation_speed * 1000:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.walking_sprites)
        return result
    
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

    def update(self, delta_time):
        """Update unit state and animation"""
        super().update(delta_time)
        if self.status == unitStatus.IDLE:
            self.current_frame = 0
        delta_time = 1 / 60  # Exemple de 60 FPS pour gérer le temps
        
        if self.status == unitStatus.BUILDING:
            self.update_building(delta_time)
        elif self.status == unitStatus.GATHERING:
            self.gather_resources(self.current_resource_type, delta_time)
