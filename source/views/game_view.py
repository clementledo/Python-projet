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

    def screen_to_world(self, screen_x, screen_y, camera_x, camera_y):
        """Inverse de world_to_screen, retourne (x, y) en coordonnées cartésiennes."""
        tile_width = self.tile_size * 2
        tile_height = self.tile_size
        # Annuler le décalage central de la carte
        screen_x -= self.viewport_width // 2
        screen_y -= self.viewport_height // 4
        # Retrouver les coordonnées iso
        # iso_x = (x - y) * tile_width // 2 - camera_x
        # iso_y = (x + y) * tile_height // 2 - camera_y
        # On applique la formule inverse
        x = ((screen_x + camera_x) // (tile_width // 2) + (screen_y + camera_y) // (tile_height // 2)) // 2
        y = ((screen_y + camera_y) // (tile_height // 2) - (screen_x + camera_x) // (tile_width // 2)) // 2
        return x, y
    
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

        # Calcul du rectangle visible en coordonnées cartésiennes
        min_x, min_y = self.screen_to_world(0, 0, camera_x, camera_y)
        max_x, max_y = self.screen_to_world(screen_width, screen_height, camera_x, camera_y)
        min_x, min_y = int(min_x), int(min_y)
        max_x, max_y = int(max_x), int(max_y)

        padding_x = int(screen_width / tile_width)
        padding_y = int(screen_height / tile_height)

        # Bornes valides
        min_x = max(min_x - padding_x, 0)
        min_y = max(min_y - padding_y, 0)
        max_x = min(max_x + padding_x, map_width - 1)
        max_y = min(max_y + padding_y, map_height - 1)

        # Première boucle : dessiner le terrain
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                tile = carte.get_tile(x, y)
                if not tile:
                    continue
                iso_x, iso_y = self.world_to_screen(x, y, camera_x, camera_y)
                terrain_texture = textures.get(tile.terrain_type, textures[Terrain_type.GRASS])
                self.screen.blit(terrain_texture, (iso_x, iso_y))
        # Deuxième boucle : dessiner les ressources
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                tile = carte.get_tile(x, y)
                if not tile or not tile.has_resource():
                    continue
                iso_x, iso_y = self.world_to_screen(x, y, camera_x, camera_y)
                if tile.resource.is_wood():
                    tree_offset_y = tile_height // 0.47
                    tree_offset_x = tile_width // 2
                    resource_texture = self.asset_manager.wood_sprites['tree']
                    self.screen.blit(resource_texture, (iso_x - tree_offset_x, iso_y - tree_offset_y))
                elif tile.resource.is_gold():
                    gold_offset_y = -tile_height // 2.8
                    gold_offset_x = -tile_width // 3
                    resource_texture = self.asset_manager.gold_sprites['gold']
                    self.screen.blit(resource_texture, (iso_x + 0, iso_y + gold_offset_y))

    def render_game(self, carte, camera_x, camera_y, clock):
        """Render the game to the screen avec un compteur de FPS."""
        self.render_map(carte, camera_x, camera_y)
        fps = clock.get_fps()
        fps_text = self.font.render(f"FPS: {int(fps)}", True, pygame.Color('white'))
        self.screen.blit(fps_text, (10, 10))
        self.dirty_rects = []