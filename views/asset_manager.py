import pygame
import os
from models.Resources.Terrain_type import Terrain_type

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
        self.building_sprites = {}
        self.terrain_textures = {}
        self.broken_building_sprites = {}
        self.ui_assets = {}  # Add UI assets dictionary
        self.villager_sprites = {
            'walking': [],
            'standing': [],
            'building': []
        }
        self.archer_sprites = {
            'attack': [],
            'walking': [],
            'standing': []
        }
        self.scout_sprites = {
            'attack': [],
            'walking': [],
            'standing': []
        }
        
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
        self.load_ui_elements()
        self.load_terrain_textures()
        self.load_decoration_sprites()
        self.load_villager_sprites()
        self.load_building_sprites()
        self.load_archer_sprites()  # Add archer sprites loading
        self.load_scout_sprites()  # Add scout sprites loading

    def load_ui_elements(self):
        self.ui_assets = {
            'resource_panel': pygame.image.load('assets/resourcecivpanel.png').convert_alpha(),
            'icons': {
                "food": pygame.image.load("assets/iconfood.png").convert_alpha(),
                "wood": pygame.image.load("assets/iconwood.png").convert_alpha(),
                "gold": pygame.image.load("assets/icongold.png").convert_alpha()
            }
        }

    def load_terrain_textures(self):
        self.terrain_textures = {
            Terrain_type.GRASS: pygame.image.load('assets/t_grass.png').convert_alpha(),
            Terrain_type.WATER: pygame.image.load('assets/t_water.png').convert_alpha(),
            # Add other terrain types here
        }

    def get_terrain_texture(self, terrain_type):
        """Get texture for specified terrain type"""
        if terrain_type not in self.terrain_textures:
            return self.terrain_textures[Terrain_type.GRASS]  # Default fallback
        return self.terrain_textures[terrain_type]

    def load_decoration_sprites(self):
        self.decoration_sprites = {
            'tree': pygame.image.load('assets/tree.png').convert_alpha(),
        }

    def load_villager_sprites(self):
        # Load building sprites
        for i in range(1, 76):  # 1 to 75
            sprite_path = f'assets/Sprites/Villager/FarmingVillager/Build & Repair/Act/Villageract{i:03d}.png'
            try:
                sprite = pygame.image.load(sprite_path).convert_alpha()
                self.villager_sprites['building'].append(sprite)
            except pygame.error as e:
                print(f"Error loading building sprite {i}: {e}")

        # Load walking sprites
        sprite_dir = "assets/Sprites/Villager/Walk"
        for i in range(16, 76):
            sprite_path = os.path.join(sprite_dir, f"Villagerwalk{i:03d}.png")
            try:
                sprite = pygame.image.load(sprite_path).convert_alpha()
                self.villager_sprites['walking'].append(sprite)
            except pygame.error as e:
                print(f"Couldn't load sprite: {sprite_path}")

        # Load standing sprites
        sprite_dir = "assets/Sprites/Villager/Stand"
        for i in range(53, 75):
            sprite_path = os.path.join(sprite_dir, f"Villagerstand{i:03d}.png")
            try:
                sprite = pygame.image.load(sprite_path).convert_alpha()
                self.villager_sprites['standing'].append(sprite)
            except pygame.error as e:
                print(f"Couldn't load sprite: {sprite_path}")

    def get_villager_sprites(self, animation_type):
        return self.villager_sprites.get(animation_type, [])

    def get_ui_asset(self, asset_name):
        return self.ui_assets.get(asset_name)

    def get_resource_icon(self, resource_type):
        return self.ui_assets['icons'].get(resource_type.lower())

    def load_building_sprites(self):
        """Load building sprites"""
        building_types = ['Towncenter', 'House', 'Barracks']  # Add all building types
        for building in building_types:
            self.building_sprites[building] = pygame.image.load(f"assets/Buildings/{building}.png").convert_alpha()
            
        # Load broken building sprites
        # Assuming max size is 4
            self.broken_building_sprites[1] = pygame.image.load(f"assets/Buildings/broken/broken_building_1.png").convert_alpha()

    def get_building_sprite(self, building_name):
        return self.building_sprites.get(building_name)

    def get_broken_building_sprite(self, size):
        return self.broken_building_sprites.get(size)

    def load_archer_sprites(self):
        # Load attack animation frames
        for i in range(1, 51):  # 1 to 50
            frame_number = str(i).zfill(3)  # Converts 1 to 001, 2 to 002, etc.
            path = f'assets/Sprites/Archer/Attack/Archerattack{frame_number}.png'
            try:
                sprite = pygame.image.load(path).convert_alpha()
                self.archer_sprites['attack'].append(sprite)
            except pygame.error:
                print(f"Could not load archer sprite: {path}")

    def load_scout_sprites(self):
        for i in range(1, 51):  # 1 to 50
            frame_number = str(i).zfill(3)  # Convert to 001, 002, etc.
            path = f'assets/Sprites/Scout/Attack/Scoutattack{frame_number}.png'
            try:
                sprite = pygame.image.load(path).convert_alpha()
                self.scout_sprites['attack'].append(sprite)
            except pygame.error:
                print(f"Could not load scout sprite: {path}")