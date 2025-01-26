import pygame
import os
from models.Resources.resource_type import ResourceType
from models.Resources.terrain_type import Terrain_type

class AssetManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AssetManager, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if self.initialized:
            return
            
        # Initialize empty sprite containers regardless of mode
        self.terrain_textures = {}
        
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

    def load_terrain_textures(self):
        self.terrain_textures = {
            Terrain_type.GRASS: pygame.image.load('assets/t_grass.png').convert_alpha(),
            # Add other terrain types here
        }

    def get_terrain_texture(self, terrain_type):
        """Get texture for specified terrain type"""
        if terrain_type not in self.terrain_textures:
            return self.terrain_textures[ResourceType.GRASS]
        return self.terrain_textures[terrain_type]