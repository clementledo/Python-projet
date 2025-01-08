import pygame
from models.Resources.Terrain_type import Terrain_type
import random
import math

class GameView:
    def __init__(self, screen, tile_size=32):
        self.screen = screen
        self.tile_size = tile_size
        self.unit_sprites = {}
        self.building_sprites = {}
        
        # Load resource panel and icons
        self.resource_panel = pygame.image.load('assets/resourcecivpanel.png').convert_alpha()
        self.resource_icons = {
            "food": pygame.image.load("assets/iconfood.png").convert_alpha(),
            "wood": pygame.image.load("assets/iconwood.png").convert_alpha(),
            "gold": pygame.image.load("assets/icongold.png").convert_alpha()
        }
        self.font = pygame.font.SysFont('Arial', 24)
        self.decorations = []  # Liste pour stocker les décorations générées
        self.decorations_generated = False  # Flag pour vérifier si les décorations ont été générées
        self.iso_offset_x = 0  # Store isometric offset
        self.iso_offset_y = 0  # Store isometric offset
    
    def generate_resources(self, carte):
        """Génère une liste de décorations (arbres, broussailles et or) sans écraser les ressources."""
        if getattr(self, "decorations_generated", False):  # Si déjà généré, ne rien faire
            return

        self.decorations = []  # Réinitialiser la liste des décorations

        for y in range(carte.hauteur):
            for x in range(carte.largeur):
                tile = carte.grille[y][x]

                if tile.resource:  # Ne pas ajouter de décorations sur des cases avec des ressources
                    match tile.resource.resource_type:
                        case "Wood":
                            tree = {
                                'type': 'tree',
                                'x': x,
                                'y': y,
                                'image': pygame.image.load('assets/tree.png').convert_alpha()
                            }
                            self.decorations.append(tree)
                        case "Gold":
                            gold = {
                                'type': 'gold',
                                'x': x,
                                'y': y,
                                'image': pygame.image.load('assets/Gold.png').convert_alpha()
                            }
                            self.decorations.append(gold)
                        case _:
                            continue

               
               
                    

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
        """
        Rendu de la carte avec gestion des textures, caméra et décorations.
        
        Args:
            carte: La carte contenant les tuiles.
            camera_x, camera_y: Position de la caméra.
            zoom_level: Niveau de zoom (1.0 = taille normale).
        """
        textures = {
            Terrain_type.GRASS: pygame.image.load('assets/t_grass.png').convert_alpha(),
            Terrain_type.WATER: pygame.image.load('assets/t_water.png').convert_alpha(),
        }

        # Dimensions des tuiles après application du zoom
        tile_width = int(self.tile_size * 2 * zoom_level)
        tile_height = int(self.tile_size * zoom_level)

        # Redimensionner les textures en fonction du zoom
        for terrain, texture in textures.items():
            textures[terrain] = pygame.transform.scale(texture, (tile_width, tile_height))

        screen_width, screen_height = self.screen.get_size()

        # Vérifier les dimensions de la grille avant de parcourir
        if not carte.grille or not carte.grille[0]:
            print("Erreur : La grille est vide ou mal initialisée.")
            return

        # Dimensions de la carte
        map_width = len(carte.grille[0])  # Nombre de colonnes
        map_height = len(carte.grille)   # Nombre de lignes

        # Rendu des tuiles
        for y in range(map_height):
            for x in range(map_width):
                if not (0 <= x < map_width and 0 <= y < map_height):
                    continue

                tile = carte.grille[y][x]
                if not tile:
                    continue

                # Convertir les coordonnées du monde en coordonnées écran
                iso_x, iso_y = self.world_to_screen(x, y, camera_x, camera_y, zoom_level)
                
                # Centrer la carte sur l'écran
                iso_x += screen_width // 2
                iso_y += screen_height // 4

                # Obtenir la texture de terrain
                terrain_texture = textures.get(tile.terrain_type, textures[Terrain_type.GRASS])
                self.screen.blit(terrain_texture, (iso_x, iso_y))

                # Dessiner un point au centre de la tuile
                point_color = (0, 255, 0)  # Vert pour les centres
                point_radius = max(2, int(2 * zoom_level))  # Taille ajustée au zoom
                pygame.draw.circle(
                    self.screen,
                    point_color,
                    (iso_x + tile_width // 2, iso_y + tile_height // 2),
                    point_radius
                )

        # Rendu des décorations (arbres, buissons, etc.)
        for decoration in self.decorations:
            x, y = decoration['x'], decoration['y']
            if not (0 <= x < map_width and 0 <= y < map_height):
                continue

            iso_x, iso_y = self.world_to_screen(x, y, camera_x, camera_y, zoom_level)
            
            # Centrer la carte et ajuster la hauteur des décorations
            iso_x += screen_width // 2
            iso_y += screen_height // 4 - tile_height

            # Redimensionner et dessiner la décoration
            decoration_image = pygame.transform.scale(
                decoration['image'], (tile_width, tile_height * 2)
            )
            self.screen.blit(decoration_image, (iso_x, iso_y))

        # Render resource panel last (on top)
        if hasattr(carte, 'resources'):
            self.render_resources(carte.resources)


    def render_minimap(self, map_data, camera_x, camera_y, zoom_level, units, buildings):
        """
        Rendu avancé de la minimap avec le terrain, les unités et les bâtiments.
        
        Args:
            map_data: Carte contenant les données de la grille.
            camera_x, camera_y: Position de la caméra.
            zoom_level: Niveau de zoom.
            units: Liste des unités avec leurs positions.
            buildings: Liste des bâtiments avec leurs positions et tailles.
        """
        # Dimensions de la minimap
        minimap_width = 200
        minimap_height = 200
        minimap_x = self.screen.get_width() - minimap_width - 10
        minimap_y = self.screen.get_height() - minimap_height - 10

        # Couleurs des terrains
        terrain_colors = {
            Terrain_type.GRASS: (34, 139, 34),  # Vert pour l'herbe
            Terrain_type.WATER: (65, 105, 225),  # Bleu pour l'eau
        }

        # Surface de la minimap
        minimap_surface = pygame.Surface((minimap_width, minimap_height))
        minimap_surface.fill((50, 50, 50))  # Fond sombre

        # Taille des tuiles sur la minimap
        tile_width = minimap_width / map_data.largeur
        tile_height = minimap_height / map_data.hauteur

        # Rendu du terrain
        for y in range(map_data.hauteur):
            for x in range(map_data.largeur):
                tile = map_data.grille[y][x]
                if tile:
                    color = terrain_colors.get(tile.terrain_type, (100, 100, 100))  # Gris par défaut
                    pygame.draw.rect(
                        minimap_surface, 
                        color, 
                        (x * tile_width, y * tile_height, tile_width, tile_height)
                    )

        # Rendu des unités
        for unit in units:
            ux, uy = unit.get_position()
            unit_color = {
                'villager': (255, 0, 0),  # Rouge pour les villageois
                'archer': (0, 0, 255),    # Bleu pour les archers
            }.get(unit.unit_type, (255, 255, 255))  # Blanc par défaut
            
            pygame.draw.rect(
                minimap_surface,
                unit_color,
                (ux * tile_width, uy * tile_height, tile_width, tile_height)
            )

        # Rendu des bâtiments
        for building in buildings:
            bx, by = building.pos
            building_width = building.size[0]-2.5  # Largeur du bâtiment en tuiles
            building_height = building.size[1]-2.5  # Hauteur du bâtiment en tuiles

            building_color = (255, 0, 0)  # Vert pour les bâtiments
            
            pygame.draw.rect(
                minimap_surface,
                building_color,
                (bx * tile_width, by * tile_height, building_width * tile_width, building_height * tile_height)
            )

        # Rectangle représentant le champ de vision de la caméra
        map_width_ratio = minimap_width / (map_data.largeur * self.tile_size)
        map_height_ratio = minimap_height / (map_data.hauteur * self.tile_size)
        
        camera_rect_width = self.screen.get_width() * map_width_ratio / zoom_level
        camera_rect_height = self.screen.get_height() * map_height_ratio / zoom_level
        camera_rect_x = camera_x * map_width_ratio
        camera_rect_y = camera_y * map_height_ratio

        # Dessiner le rectangle de la caméra
        camera_rect = pygame.Rect(camera_rect_x, camera_rect_y, camera_rect_width, camera_rect_height)
        pygame.draw.rect(minimap_surface, (255, 255, 255), camera_rect, 2)

        # Afficher la minimap sur l'écran
        self.screen.blit(minimap_surface, (minimap_x, minimap_y))

        # Bordure de la minimap
        pygame.draw.rect(
            self.screen,
            (100, 100, 100),
            (minimap_x, minimap_y, minimap_width, minimap_height),
            2
    )


    def render_units(self, units, camera_x, camera_y, zoom_level,selected_unit):
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

            #Highlight the selected unit
            if selected_unit == unit:
                highlight_color = (255, 255, 0)  # Yellow highlight
                highlight_radius = int(tile_width * 0.5)  # Adjust as needed
                pygame.draw.circle(self.screen, highlight_color, 
                                (iso_x, iso_y + tile_height // 2), highlight_radius, 2)

            sprite = self.unit_sprites.get(unit.unit_type)
            if sprite:
                scaled_sprite = pygame.transform.scale(sprite, 
                    (int(sprite.get_width() * zoom_level), int(sprite.get_height() * zoom_level)))
                
                # Center unit on tile
                self.screen.blit(scaled_sprite, 
                    (iso_x - scaled_sprite.get_width() // 2, 
                     iso_y - scaled_sprite.get_height() // 2))
                self.draw_health_bar(self.screen, unit, iso_x, iso_y, zoom_level)
        
    def load_unit_sprite(self, unit_type, image_path):
        """Charge un sprite d'unité."""
        image = pygame.image.load(image_path).convert_alpha()
        self.unit_sprites[unit_type] = image

    def load_building_sprite(self, building_name, sprite_path):
        """Charge l'image du bâtiment à partir du chemin donné."""
        self.building_sprites[building_name] = pygame.image.load(sprite_path).convert_alpha()

    def render_buildings(self, buildings, camera_x, camera_y, zoom_level):
        for building in buildings:
            # Get building properties
            building_x, building_y = building.pos
            building_size_x, building_size_y = building.size
            
            # Calculate required size in pixels based on tiles to occupy
            required_width = self.tile_size * building_size_x * zoom_level
            required_height = self.tile_size * building_size_y * zoom_level

            # Scale building sprite to match required tile coverage
            scaled_image = pygame.transform.scale(
                building.image, 
                (int(required_width), int(required_height))
            )

            # Calculate final position for centered building
            main_iso_x, main_iso_y = self.world_to_screen(building_x, building_y, camera_x, camera_y, zoom_level)
            screen_width, screen_height = self.screen.get_size()
            main_iso_x += screen_width // 2 - (required_width // 4)  # Adjust for isometric view
            main_iso_y += screen_height // 4 - (required_height // 4)

            # Draw building sprite
            self.screen.blit(scaled_image, (main_iso_x, main_iso_y))

    def draw_health_bar(self, surface, unit, x, y, zoom_level=1.0):
        """Dessine une barre de vie proportionnelle aux PV de l'unité avec zoom"""
        # Ratios pour les dimensions avec zoom
        LARGEUR_BARRE = self.tile_size * 0.8 * zoom_level
        HAUTEUR_BARRE = max(2, self.tile_size * 0.08 * zoom_level)
        OFFSET_Y = self.tile_size * 0.2 * zoom_level
        BORDER = max(1, int(zoom_level))  # Épaisseur du contour
        
        # Position de la barre
        pos_x = x - 12 + (self.tile_size * zoom_level - LARGEUR_BARRE) / 8
        pos_y = y - 3*OFFSET_Y
        
        # Dessiner le contour noir
        pygame.draw.rect(surface, (0, 20, 0), 
                        (pos_x - BORDER, pos_y - BORDER, 
                         LARGEUR_BARRE + 2*BORDER, HAUTEUR_BARRE + 2*BORDER))
        
        # Barre rouge (fond)
        pygame.draw.rect(surface, (200, 0, 0), 
                        (pos_x, pos_y, LARGEUR_BARRE, HAUTEUR_BARRE))
        
        # Barre verte (PV restants)
        if unit.health > 0:
            ratio_pv = unit.health / unit.max_health
            pygame.draw.rect(surface, (0, 190, 0),
                           (pos_x, pos_y, LARGEUR_BARRE * ratio_pv, HAUTEUR_BARRE))

    def draw_unit(self, surface, unit, x, y, zoom_level=1.0):
        # ...existing code...
        self.draw_health_bar(surface, unit, x, y, zoom_level)

    def render_resources(self, resources):
        """Display resource panel with current resources"""
        # Panel position at top of screen
        panel_x = 1220
        panel_y = 10
        
        # Scale panel to reasonable size
        panel_width = 700
        panel_height = 80
        scaled_panel = pygame.transform.scale(self.resource_panel, (panel_width, panel_height))
        self.screen.blit(scaled_panel, (panel_x, panel_y))

        # Resource icon size and spacing
        icon_size = 40
        spacing = 150
        
        # Display each resource (using lowercase keys)
        for i, (resource_type, amount) in enumerate(resources.items()):
            # Position for this resource
            x = panel_x + 40 + (i *spacing)
            y = panel_y + 15
            
            # Draw icon (ensure lowercase key)
            resource_type = resource_type.lower()
            icon = pygame.transform.scale(self.resource_icons[resource_type], (icon_size, icon_size))
            self.screen.blit(icon, (x, y))
            
            # Draw amount
            text = self.font.render(str(amount), True, (255, 255, 255))
            self.screen.blit(text, (x + icon_size + 20, y + 8))


