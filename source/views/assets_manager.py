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
        self.load_building_sprites()
        self.load_villager_sprites()

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

    def load_building_sprites(self):
        try:
            # Assurez-vous que la clé correspond exactement au nom du bâtiment
            self.building_sprites['Town Centre'] = pygame.image.load('assets/buildings/town_center.png').convert_alpha()
            print("Sprite Town Centre chargé avec succès")

            original_stable = pygame.image.load('assets/buildings/Stable.png').convert_alpha()
            scaled_width = int(original_stable.get_width() * 1.5)
            scaled_height = int(original_stable.get_height() * 1.5)
            self.building_sprites['Stable'] = pygame.transform.scale(original_stable, (scaled_width, scaled_height))

            original_barracks = pygame.image.load('assets/buildings/Barracks.png').convert_alpha()
            scaled_width = int(original_barracks.get_width() / 1.45)
            scaled_height = int(original_barracks.get_height() / 1.45)
            self.building_sprites['Barracks'] = pygame.transform.scale(original_barracks, (scaled_width, scaled_height))

            # Corriger l'ajout de l'Archery Range au dictionnaire
            self.building_sprites['Archery Range'] = pygame.image.load('assets/buildings/Archery_range.png').convert_alpha()
            print("Sprite ArcheryRange chargé avec succès")

        except pygame.error as e:
            print(f"Erreur de chargement des sprites des bâtiments : {e}")  

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
    
    def apply_tint(self, image, tint_color):
        """Appliquer une teinte de couleur à une image"""
        tinted_image = image.copy()
        # Créer une surface de la même taille avec la couleur de teinte
        tint_surface = pygame.Surface(tinted_image.get_size(), pygame.SRCALPHA)
        tint_surface.fill(tint_color)
        # Appliquer la surface de teinte avec un mode de fusion approprié
        tinted_image.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return tinted_image