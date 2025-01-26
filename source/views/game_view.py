import pygame
from models.Resources.terrain_type import Terrain_type

class GameView:
    def __init__(self, screen, tile_size=50, asset_manager=None):
        self.screen = screen
        self.tile_size = tile_size
        self.asset_manager = asset_manager
        self.unit_sprites = {}
        self.building_sprites = {}
        
        self.font = pygame.font.SysFont('Arial', 24)
        self.decorations = []  # Liste pour stocker les décorations générées
        self.decorations_generated = False  # Flag pour vérifier si les décorations ont été générées

        # Cache for transformed sprites
        self.sprite_cache = {}
        
        # Viewport properties
        self.viewport_width = screen.get_width()
        self.viewport_height = screen.get_height()
        
        # Dirty rectangles for partial updates
        self.dirty_rects = []

    def world_to_screen(self, x, y, camera_x, camera_y):
        """Convert world coordinates to screen coordinates with isometric projection."""
        tile_width = self.tile_size * 2
        tile_height = self.tile_size 

        iso_x = (x - y) * tile_width // 2 - camera_x
        iso_y = (x + y) * tile_height // 2 - camera_y

        return iso_x, iso_y
    
    def screen_to_world(self, x, y, camera_x, camera_y):
        """Convert screen coordinates to world coordinates with isometric projection."""
        tile_width = self.tile_size * 2
        tile_height = self.tile_size

        x += camera_x
        y += camera_y

        world_x = (2 * y + x) // tile_width
        world_y = (2 * y - x) // tile_width

        return world_x, world_y
    
    def render_map(self, carte, camera_x, camera_y):
        """Render the map to the screen."""
        base_textures = {
            Terrain_type.GRASS: self.asset_manager.terrain_textures[Terrain_type.GRASS],
        }

        # Dimensions des tuiles
        tile_width = self.tile_size * 2
        tile_height = self.tile_size

        # Redimensionner les textures de base
        textures = {
            terrain: pygame.transform.scale(texture, (tile_width, tile_height))
            for terrain, texture in base_textures.items()
        }

        # Dimensions de l'écran
        screen_width, screen_height = self.screen.get_size()

        # Dimensions de la carte
        map_width = len(carte.grid[0])  # Nombre de colonnes
        map_height = len(carte.grid)   # Nombre de lignes

        # Rendu des tuiles
        for y in range(map_height):
            for x in range(map_width):
                tile = carte.get_tile(x, y)
                if not tile:
                    continue

                # Convertir les coordonnées du monde en coordonnées écran
                iso_x, iso_y = self.world_to_screen(x, y, camera_x, camera_y)
                
                # Centrer la carte sur l'écran
                iso_x += screen_width // 2
                iso_y += screen_height // 4

                # Obtenir la texture de terrain
                terrain_texture = textures.get(tile.terrain_type, textures[Terrain_type.GRASS])
                self.screen.blit(terrain_texture, (iso_x, iso_y))

    def render_game(self, carte, camera_x, camera_y, clock):
        """Render the game to the screen avec un compteur de FPS."""
        self.render_map(carte, camera_x, camera_y)
        fps = clock.get_fps()
        fps_text = self.font.render(f"FPS: {int(fps)}", True, pygame.Color('white'))
        self.screen.blit(fps_text, (10, 10))
        self.dirty_rects = []

        #afficher position de la camera en dessous du compteur de FPS
        camera_pos = self.font.render(f"Camera: {int(camera_x)}, {int(camera_y)}", True, pygame.Color('white'))
        self.screen.blit(camera_pos, (10, 40))
     