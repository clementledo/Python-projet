import pygame
from models.Resources.Terrain_type import Terrain_type
import random
import math

class GameView:
    def __init__(self, screen, tile_size=32):
        # ... (existing initialization code) ...
        self.screen = screen
        self.unit_sprites = {}  # Dictionnaire pour stocker les images des unités
        self.tile_size = tile_size  # Taille de chaque tuile en pixels
        self.decorations = []  # Liste pour stocker les décorations générées
        self.decorations_generated = False  # Flag pour vérifier si les décorations ont été générées
        self.font = pygame.font.SysFont('Arial', 36)
        self.iso_offset_x = 0  # Store isometric offset
        self.iso_offset_y = 0  # Store isometric offset
    
    def generate_decorations(self, carte):
        """Génère une liste de décorations (arbres et broussailles) au début."""
        if getattr(self, "decorations_generated", False):  # Si les décorations ont déjà été générées, on ne fait rien
            return
        
        self.decorations = []  # Réinitialiser la liste des décorations
        for x in range(carte.largeur):
            for y in range(carte.hauteur):
                tile = carte.grille[x][y]
                
                if tile.terrain_type == Terrain_type.GRASS:
                    random_value = random.random()
                    
                    # Générer un arbre avec une probabilité de 0.8%
                    if random_value < 0.008:
                        tree = {
                            'type': 'tree',
                            'x': x,
                            'y': y,
                            'image': pygame.image.load('assets/tree.png').convert_alpha()
                        }
                        self.decorations.append(tree)
                    
                    # Générer une broussaille avec une probabilité de 0.4%
                    elif random_value < 0.012:  # Probabilité cumulée (1.2%)
                        bush = {
                            'type': 'bush',
                            'x': x,
                            'y': y,
                            'image': pygame.image.load('assets/bush.png').convert_alpha()
                        }
                        self.decorations.append(bush)
                    # Générer Gold avec une probabilité de 0.3%  
                    #elif random_value < 0.015:  # Probabilité cumulée (1.5%)
                       # gold = {
                           # 'type': 'gold',
                           # 'x': x,
                           # 'y': y,
                           # 'image': pygame.image.load('assets/Gold.png').convert_alpha()
                       # }
                        #self.decorations.append(gold)

        # Marquer que les décorations ont été générées
        self.decorations_generated = True


    def world_to_screen(self, x, y, camera_x, camera_y, zoom_level):
        """Convert world coordinates to screen coordinates with isometric projection."""
        tile_width = int(self.tile_size * 2 * zoom_level)
        tile_height = int(self.tile_size * zoom_level)
        
        # Isometric conversion
        iso_x = (x - y) * tile_width // 2 - camera_x
        iso_y = (x + y) * tile_height // 2 - camera_y
        
        return iso_x, iso_y

    def render_map(self, carte, camera_x, camera_y, zoom_level):
        textures = {
            Terrain_type.GRASS: pygame.image.load('assets/t_grass.png').convert_alpha(),
            Terrain_type.WATER: pygame.image.load('assets/t_water.png').convert_alpha(),
        }

        # Tile dimensions after zoom
        tile_width = int(self.tile_size * 2 * zoom_level)
        tile_height = int(self.tile_size * zoom_level)

        # Resize textures
        for terrain, texture in textures.items():
            textures[terrain] = pygame.transform.scale(texture, (tile_width, tile_height))

        screen_width, screen_height = self.screen.get_size()

        # Render tiles across the entire map
        for x in range(carte.largeur):
            for y in range(carte.hauteur):
                tile = carte.grille[x][y]
                if not tile:
                    continue

                # Convert world to screen coordinates
                iso_x, iso_y = self.world_to_screen(x, y, camera_x, camera_y, zoom_level)
                
                # Center the map
                iso_x += screen_width // 2
                iso_y += screen_height // 4

                # Draw terrain tile
                terrain_texture = textures.get(tile.terrain_type, textures[Terrain_type.GRASS])
                self.screen.blit(terrain_texture, (iso_x, iso_y))

        # Render decorations with same isometric conversion
        for decoration in self.decorations:
            x, y = decoration['x'], decoration['y']
            iso_x, iso_y = self.world_to_screen(x, y, camera_x, camera_y, zoom_level)
            
            # Center the map and adjust for decoration height
            iso_x += screen_width // 2
            iso_y += screen_height // 4 - tile_height

            # Scale and render decoration
            tree_scaled = pygame.transform.scale(decoration['image'], (tile_width, tile_height * 2))
            self.screen.blit(tree_scaled, (iso_x, iso_y))

    def render_minimap(self, map_data, camera_x, camera_y, zoom_level,units):
        """Advanced minimap rendering with terrain and unit representation."""
        minimap_width = 200  # Increased size for better visibility
        minimap_height = 200
        minimap_x = self.screen.get_width() - minimap_width - 10
        minimap_y = self.screen.get_height() - minimap_height - 10

        # Terrain color mapping
        terrain_colors = {
            Terrain_type.GRASS: (34, 139, 34),    # Forest Green
            Terrain_type.WATER: (65, 105, 225),   # Royal Blue
            # Add more terrain types as needed
        }

        # Create a surface for the minimap
        minimap_surface = pygame.Surface((minimap_width, minimap_height))
        minimap_surface.fill((50, 50, 50))  # Dark background

        # Calculate tile sizes
        tile_width = minimap_width / map_data.largeur
        tile_height = minimap_height / map_data.hauteur

        # Render terrain
        for x in range(map_data.largeur):
            for y in range(map_data.hauteur):
                tile = map_data.grille[x][y]
                if tile:
                    color = terrain_colors.get(tile.terrain_type, (100, 100, 100))
                    pygame.draw.rect(minimap_surface, color, 
                        (x * tile_width, y * tile_height, tile_width, tile_height))

    
        # Render units
        for unit in units:
            x, y = unit.get_position()
            unit_color = {
                'villager': (255, 0, 0),    # Red for villagers
                'archer': (0, 0, 255)        # Blue for archers
            }.get(unit.unit_type, (255, 255, 255))  # White as default
            
            pygame.draw.rect(minimap_surface, unit_color, 
                (x * tile_width, y * tile_height, tile_width, tile_height))

        # Render camera view rectangle
        map_width_ratio = minimap_width / (map_data.largeur * self.tile_size)
        map_height_ratio = minimap_height / (map_data.hauteur * self.tile_size)
        
        camera_rect_width = self.screen.get_width() * map_width_ratio / zoom_level
        camera_rect_height = self.screen.get_height() * map_height_ratio / zoom_level
        camera_rect_x = camera_x * map_width_ratio
        camera_rect_y = camera_y * map_height_ratio

        # Draw camera rectangle
        camera_rect = pygame.Rect(camera_rect_x, camera_rect_y, 
                                camera_rect_width, camera_rect_height)
        pygame.draw.rect(minimap_surface, (255, 255, 255), camera_rect, 2)

        # Blit minimap to screen
        self.screen.blit(minimap_surface, (minimap_x, minimap_y))

        # Optional: add border
        pygame.draw.rect(self.screen, (100, 100, 100), 
                        (minimap_x, minimap_y, minimap_width, minimap_height), 2)

    def render_units(self, units, camera_x, camera_y, zoom_level):
        """Improved unit rendering with isometric projection."""
        tile_width = int(self.tile_size * 2 * zoom_level)
        tile_height = int(self.tile_size * zoom_level)

        screen_width, screen_height = self.screen.get_size()

        for unit in sorted(units, key=lambda u: u.get_position()[1]):
            x_tile, y_tile = unit.get_position()

            # Convert world to screen coordinates
            iso_x, iso_y = self.world_to_screen(x_tile, y_tile, camera_x, camera_y, zoom_level)
            
            # Center the map
            iso_x += screen_width // 2
            iso_y += screen_height // 4

            sprite = self.unit_sprites.get(unit.unit_type)
            if sprite:
                scaled_sprite = pygame.transform.scale(sprite, 
                    (int(sprite.get_width() * zoom_level), int(sprite.get_height() * zoom_level)))
                
                # Center unit on tile
                self.screen.blit(scaled_sprite, 
                    (iso_x - scaled_sprite.get_width() // 2, 
                     iso_y - scaled_sprite.get_height() // 2))
        
    def load_unit_sprite(self, unit_type, image_path):
        """Charge un sprite d'unité."""
        image = pygame.image.load(image_path).convert_alpha()
        self.unit_sprites[unit_type] = image