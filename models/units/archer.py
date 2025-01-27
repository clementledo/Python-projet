from .unit import Unit
from .unit import unitStatus
from views.asset_manager import AssetManager

class Archer(Unit):
    def __init__(self, x, y, map_instance,player_id=1, use_terminal_view=False):
        super().__init__(x, y, unit_type="Archer", attack_speed=4, speed=1.0, hp=30, map=map_instance)
        self.cost = {"wood": 25, "gold": 45}
        self.training_time = 35
        self.attack_range = 4
        self.player_id = player_id
        self.use_terminal_view = use_terminal_view
        self.sprites_initialized = False

    def initialize_sprites(self):
        if self.use_terminal_view:
            self.sprites_initialized = True
            return

        if self.sprites_initialized:
            return
        import pygame

        self.asset_manager = AssetManager()
        self.attack_sprites = self.asset_manager.archer_sprites.get('attack', [])
        self.walking_sprites = self.asset_manager.archer_sprites.get('walking', [])
        self.standing_sprites = self.asset_manager.archer_sprites.get('standing', [])
        
        self.current_frame = 0
        self.animation_speed = 0.6
        self.last_update = pygame.time.get_ticks()
        self.sprites_initialized = True

    def get_current_sprite(self):
        if self.use_terminal_view:
            return None
        
        import pygame
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_speed * 1000:
            self.last_update = now
        
        if not self.sprites_initialized:
            self.initialize_sprites()
            
        if self.status == unitStatus.ATTACKING and self.attack_sprites:
            return self.attack_sprites[self.current_frame]
        elif self.status == unitStatus.MOVING and self.walking_sprites:
            return self.walking_sprites[self.current_frame]
        elif self.standing_sprites:
            return self.standing_sprites[self.current_frame]
        
        return None