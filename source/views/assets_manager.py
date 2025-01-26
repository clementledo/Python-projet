import os
import pygame
from models.Resources.terrain_type import Terrain_type

class AssetManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AssetManager, cls).__new__(cls, *args, **kwargs)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if self.initialized:
            return
            
        # Initialize empty sprite containers regardless of mode
        self.building_sprites = {}
        self.terrain_textures = {}
        self.broken_building_sprites = {}
        self.ui_assets = {}  # Add UI assets dictionary
        self.villager_sprites = {
            'walking': [],
            'standing': [],
            'building': []
        }
        self.wood_sprites = {}
        self.gold_sprites = {}
        
        self.use_terminal_view = False
        # Skip asset loading in terminal mode
        if 'SDL_VIDEODRIVER' in os.environ and os.environ['SDL_VIDEODRIVER'] == 'dummy':
            self.use_terminal_view = True
            self.initialized = True
            return
            
        # Only load assets in GUI mode
        self.load_all_assets()
        self.initialized = True

    def load_all_assets(self):
        self.load_terrain_textures()
        self.load_wood_sprites()
        self.load_gold_sprites()

    def load_terrain_textures(self):
        self.terrain_textures = {
            Terrain_type.GRASS: pygame.image.load('assets/t_grass.png').convert_alpha(),
            # Add other terrain types here
        }

    def get_terrain_texture(self, terrain_type):
        """Get texture for specified terrain type"""
        if terrain_type not in self.terrain_textures:
            return self.terrain_textures[Terrain_type.GRASS]
        return self.terrain_textures[terrain_type]

    def load_wood_sprites(self):
        """Load wood sprites (tree.png)"""
        try:
            self.wood_sprites['tree'] = pygame.image.load('assets/Resources/tree.png').convert_alpha()
        except pygame.error as e:
            print(f"Error loading wood sprite: assets/tree.png - {e}")

    def load_gold_sprites(self):
        """Load gold sprites (Gold.png) et les redimensionner."""
        try:
            gold_image = pygame.image.load('assets/Resources/Gold.png').convert_alpha()
            gold_image = pygame.transform.scale(gold_image, (gold_image.get_width() // 2, gold_image.get_height() // 2))
            self.gold_sprites['gold'] = gold_image
        except pygame.error as e:
            print(f"Error loading gold sprite: assets/Gold.png - {e}")