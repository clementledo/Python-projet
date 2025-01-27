from models.units.unit import Unit
from views.asset_manager import AssetManager
from models.units.unit import unitStatus

class Horseman(Unit):
    def __init__(self, x, y, map_instance, player_id=1, use_terminal_view=False):
        super().__init__(x, y, unit_type="Horseman", attack_speed=4, speed=1.2, hp=45, map=map_instance)
        self.cost = {"food": 80, "gold": 20}
        self.attack_range = 1
        self.training_time = 30
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
        # Get sprite animations from asset manager
        self.attack_sprites = self.asset_manager.scout_sprites.get('attack', [])
        self.walking_sprites = self.asset_manager.scout_sprites.get('walking', [])
        self.standing_sprites = self.asset_manager.scout_sprites.get('standing', [])
        
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