from .unit import Unit
from .unit import unitStatus
import pygame
import os
from views.asset_manager import AssetManager

class Villager(Unit):
    def __init__(self, x, y, map, player_id=1, use_terminal_view=False):
        super().__init__(x, y, "Villager", 0.3, 2, 25, map)
        self.player_id = player_id
        self.use_terminal_view = use_terminal_view
        """self.is_gathering = False"""
        self.gathering_progress = 0
        """self.gathering_speed = 1"""
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
        self.atk_power = 3  # Villager specific attack power
        self.symbol = 'V'  # For terminal display
        self.sprites_initialized = False
        self.task = None  # Add this line to initialize the task attribute

    def initialize_sprites(self):
        """Initialize sprite-related attributes and load sprites"""
        if self.use_terminal_view:
            self.sprites_initialized = True
            return

        if self.sprites_initialized:
            return

        import pygame
        self.asset_manager = AssetManager()
        
        # Safe sprite initialization with empty lists as fallback
        self.walking_sprites = self.asset_manager.villager_sprites.get('walking', [])
        self.standing_sprites = self.asset_manager.villager_sprites.get('standing', [])
        self.building_sprites = self.asset_manager.villager_sprites.get('building', [])
        
        self.current_frame = 0
        self.animation_speed = 0.6
        self.last_update = pygame.time.get_ticks()
        self.sprites_initialized = True

    def get_current_sprite(self):
        """Returns the current sprite based on unit state with safety checks"""
        if self.use_terminal_view:
            return None
            
        # Safety check for sprite initialization
        if not self.sprites_initialized:
            self.initialize_sprites()
            
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_speed * 1000:
            self.last_update = now
            
            # Safe sprite list access with bounds checking
            if self.status == unitStatus.BUILDING and self.building_sprites:
                self.current_frame = (self.current_frame + 1) % max(len(self.building_sprites), 1)
                return self.building_sprites[min(self.current_frame, len(self.building_sprites) - 1)]
            elif self.status == unitStatus.MOVING and self.walking_sprites:
                self.current_frame = (self.current_frame + 1) % max(len(self.walking_sprites), 1)
                return self.walking_sprites[min(self.current_frame, len(self.walking_sprites) - 1)]
            elif self.standing_sprites:
                self.current_frame = (self.current_frame + 1) % max(len(self.standing_sprites), 1)
                return self.standing_sprites[min(self.current_frame, len(self.standing_sprites) - 1)]
        
        # Safe return of current frame
        if self.status == unitStatus.BUILDING and self.building_sprites:
            return self.building_sprites[min(self.current_frame, len(self.building_sprites) - 1)]
        elif self.status == unitStatus.MOVING and self.walking_sprites:
            return self.walking_sprites[min(self.current_frame, len(self.walking_sprites) - 1)]
        elif self.standing_sprites:
            return self.standing_sprites[min(self.current_frame, len(self.standing_sprites) - 1)]
        
        return None  # Return None if no valid sprites available

    def move_towards(self, position, grid):
        """Handle movement and animation"""
        result = super().move_towards(position, grid)
        if result and self.status == unitStatus.MOVING and not self.use_terminal_view:
            now = pygame.time.get_ticks()
            if now - self.last_update > self.animation_speed * 1000:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.walking_sprites)
        return result
    
    def start_building(self, building, builders_count):
        """Démarre la construction d'un bâtiment."""
        self.status = unitStatus.BUILDING
        self.building = building
        self.destination = building.pos
        nominal_time = building.construction_time
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
        self.status = unitStatus.IDLE
        self.grid[self.y][self.x].resource.quantity[resource_type] -= resources_gathered
        """reste à actualiser ressources de IA"""
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
                if (tile.resource):
                    self.gathering_progress += self.gathering_speed
                    if self.gathering_progress >= 100:
                        self.carried_resources += 1
                        self.gathering_progress = 0

    """"villageois placé en amont sur la bonne tuile"""
    def collect_resource(self, resource_type) : 
        delta_time = 60
        self.start_gathering(resource_type)
        self.gather_resources(resource_type, delta_time)
        x = self.x
        y = self.y
        self.grid[y][x].resource
        
    def update(self):
        """Update unit state and animation"""
        delta_time = 1 / 60 
        super().update()
        if self.status == unitStatus.IDLE:
            self.current_frame = 0
         # Exemple de 60 FPS pour gérer le temps
        
        if self.status == unitStatus.BUILDING:
            self.update_building(delta_time)
        elif self.status == unitStatus.GATHERING:
            self.gather_resources(self.current_resource_type, delta_time)

    def serialize(self):
        """Serialize villager data"""
        base_data = super().serialize()
        villager_data = {
            "is_gathering": self.is_gathering,
            "gathering_progress": self.gathering_progress,
            "gathering_speed": self.gathering_speed,
            "carry_capacity": self.carry_capacity,
            "carried_resources": self.carried_resources,
            "resource_type": self.resource_type,
            "resource_capacity": self.resource_capacity,
            "resource_gather_rate": self.resource_gather_rate,
            "current_resources": self.current_resources,
            "current_resource_type": self.current_resource_type,
        }
        return {**base_data, **villager_data}

    @classmethod
    def deserialize(cls, data, map):
        """Deserialize villager data"""
        villager = cls(data["x"], data["y"], map, data["player_id"])
        villager.position = data["position"]
        villager.health = data["health"]
        villager.max_health = data["max_health"]
        villager.status = unitStatus(data["status"])
        villager.is_gathering = data["is_gathering"]
        villager.gathering_progress = data["gathering_progress"]
        villager.gathering_speed = data["gathering_speed"]
        villager.carry_capacity = data["carry_capacity"]
        villager.carried_resources = data["carried_resources"]
        villager.resource_type = data["resource_type"]
        villager.resource_capacity = data["resource_capacity"]
        villager.resource_gather_rate = data["resource_gather_rate"]
        villager.current_resources = data["current_resources"]
        villager.current_resource_type = data["current_resource_type"]
        return villager

    def collect_resource(self, resource_type):
        self.task = resource_type  # Set the task attribute when collecting a resource
        # ... existing code for collecting resources ...
