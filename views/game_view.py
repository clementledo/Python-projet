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
        
        self.tile_width_half = self.tile_size  # Calculé une seule fois
        self.tile_height_half = self.tile_size // 2

        # Load resources ONCE in the init
        try:
            self.resource_panel = pygame.image.load('assets/resourcecivpanel.png').convert_alpha()
            self.resource_icons = {
                "food": pygame.image.load("assets/iconfood.png").convert_alpha(),
                "wood": pygame.image.load("assets/iconwood.png").convert_alpha(),
                "gold": pygame.image.load("assets/icongold.png").convert_alpha()
            }
            self.decoration_images = {
                'tree': pygame.image.load('assets/tree.png').convert_alpha(),
                'gold': pygame.image.load('assets/Gold.png').convert_alpha(),
                # Ajouter d'autres décorations ici...
            }
        except FileNotFoundError as e:
            print(f"Error loading resources: {e}")
            # Handle the error appropriately, e.g., exit the game or use placeholder images
            raise  # Re-raise the exception to stop execution or handle it differently

        try:
            self.font = pygame.font.Font("assets/fonts/Cinzel-Regular.ttf", 24)
        except FileNotFoundError:
            self.font = pygame.font.SysFont('Arial', 24)
            print("Using default Arial font.")

        self.decorations = []
        self.decorations_generated = False
        self.iso_offset_x = 0
        self.iso_offset_y = 0
        
        self.panel_width = 700
        self.panel_height = 80
        self.icon_size = 40
        self.spacing = 150
        self.panel_x = 1220

        self.scaled_panel = pygame.transform.scale(self.resource_panel, (self.panel_width, self.panel_height))

        self.resource_text_offsets = {} #Stock les offset pour chaque type de ressource
        for resource_type in self.resource_icons:
            icon = pygame.transform.scale(self.resource_icons[resource_type], (self.icon_size, self.icon_size))
            self.resource_icons[resource_type] = icon #Met à jour les icons avec les versions scalées
            self.resource_text_offsets[resource_type] = self.icon_size + 20
            
        
        self.colorized_surfaces_cache = {}

    
    def generate_resources(self, carte):
        """Génère les décorations en utilisant les images préchargées."""
        if self.decorations_generated:
            return

        self.decorations = []

        for y in range(carte.hauteur):
            for x in range(carte.largeur):
                tile = carte.grille[y][x]

                if tile.resource:
                    match tile.resource.resource_type:
                        case "Wood":
                            decoration = {
                                'type': 'tree',
                                'x': x,
                                'y': y,
                                'image': self.decoration_images['tree'] # Utiliser l'image préchargée
                            }
                            self.decorations.append(decoration)
                        case "Gold":
                            decoration = {
                                'type': 'gold',
                                'x': x,
                                'y': y,
                                'image': self.decoration_images['gold'] # Utiliser l'image préchargée
                            }
                            self.decorations.append(decoration)
                        case _:
                            continue

        self.decorations_generated = True


    def world_to_screen(self, x, y, camera_x, camera_y, zoom_level):
        """Convertit les coordonnées du monde en coordonnées écran avec projection isométrique."""

        # Précalculer les valeurs dépendant du zoom (une seule fois par appel)
        tile_width_half_zoom = int(self.tile_width_half * zoom_level)
        tile_height_half_zoom = int(self.tile_height_half * zoom_level)

        # Conversion isométrique (encore plus optimisée)
        iso_x = (x - y) * tile_width_half_zoom - camera_x
        iso_y = (x + y) * tile_height_half_zoom - camera_y

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
            self.render_resources()



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
        

    def colorize_surface(self, surface, color):
        """Applique une teinte de couleur à une surface avec mise en cache optimisée."""
        # Utiliser un identifiant unique pour chaque surface en fonction de ses dimensions et données
        surface_key = (surface.get_size(), pygame.image.tostring(surface, "RGBA"))
        cache_key = (surface_key, color)  # Clé unique pour le cache

        # Vérifier si la surface colorisée est déjà en cache
        if cache_key in self.colorized_surfaces_cache:
            return self.colorized_surfaces_cache[cache_key]

        # Colorier la surface
        colorized = surface.copy()
        colorized.fill(color, special_flags=pygame.BLEND_RGBA_MULT)

        # Ajouter au cache
        self.colorized_surfaces_cache[cache_key] = colorized
        return colorized


    def render_units(self, units, camera_x, camera_y, zoom_level, selected_unit):
        """Improved unit rendering with isometric projection and player colors."""
        tile_width = int(self.tile_size * 2 * zoom_level)
        tile_height = int(self.tile_size * zoom_level)
        screen_width, screen_height = self.screen.get_size()

        for unit in sorted(units, key=lambda u: u.get_position()[1]):
            x_tile, y_tile = unit.get_position()
            iso_x, iso_y = self.world_to_screen(x_tile, y_tile, camera_x, camera_y, zoom_level)
            
            iso_x += screen_width // 2
            iso_y += screen_height // 4

            if selected_unit == unit:
                highlight_color = (255, 255, 0)
                highlight_radius = int(tile_width * 0.5)
                pygame.draw.circle(self.screen, highlight_color, 
                                (iso_x, iso_y + tile_height // 2), highlight_radius, 2)

            sprite = self.unit_sprites.get(unit.unit_type)
            if sprite:
                scaled_sprite = pygame.transform.scale(sprite, 
                    (int(sprite.get_width() * zoom_level), int(sprite.get_height() * zoom_level)))
                
                # Apply blue tint for Player 2 units
                if unit.player_id == 2:
                    scaled_sprite = self.colorize_surface(scaled_sprite, (100, 100, 255, 255))
                
                self.screen.blit(scaled_sprite, 
                    (iso_x - scaled_sprite.get_width() // 2, 
                    iso_y - scaled_sprite.get_height() // 2))
                self.draw_health_bar(self.screen, unit, iso_x, iso_y, zoom_level)

    def load_unit_sprite(self, unit_type, image_path):
        """Charge un sprite d'unité."""
        self.unit_sprites[unit_type] = pygame.image.load(image_path).convert_alpha()

    def load_building_sprite(self, building_name, sprite_path):
        """Charge l'image du bâtiment à partir du chemin donné."""
        self.building_sprites[building_name] = pygame.image.load(sprite_path).convert_alpha()

    def render_buildings(self, buildings, camera_x, camera_y, zoom_level):
        """Render buildings with player colors"""
        screen_width, screen_height = self.screen.get_size()
        
        for building in buildings:
            building_x, building_y = building.pos
            iso_x, iso_y = self.world_to_screen(building_x, building_y, camera_x, camera_y, zoom_level)
            
            iso_x += screen_width // 2
            iso_y += screen_height // 4
            
            sprite = self.building_sprites.get(building.symbol)
            if sprite:
                scaled_sprite = pygame.transform.scale(sprite, 
                    (int(sprite.get_width() * zoom_level), int(sprite.get_height() * zoom_level)))
                
                # Apply blue tint for Player 2 buildings
                if building.player_id == 2:
                    scaled_sprite = self.colorize_surface(scaled_sprite, (100, 100, 255, 255))
                
                self.screen.blit(scaled_sprite, (iso_x, iso_y))

    def draw_health_bar(self, surface, unit, x, y, zoom_level=1.0):
        """
        Dessine une barre de vie proportionnelle aux PV de l'unité avec zoom.
        
        Args:
            surface: Surface pygame sur laquelle dessiner
            unit: Unité dont on veut afficher la barre de vie
            x, y: Position de la barre de vie
            zoom_level: Niveau de zoom (défaut: 1.0)
        """
        # Constantes de style
        HEALTH_BAR_WIDTH_RATIO = 0.8
        HEALTH_BAR_HEIGHT_RATIO = 0.08
        VERTICAL_OFFSET_RATIO = 0.2
        HORIZONTAL_OFFSET = 12
        
        # Calcul des dimensions avec zoom
        bar_width = self.tile_size * HEALTH_BAR_WIDTH_RATIO * zoom_level
        bar_height = max(2, self.tile_size * HEALTH_BAR_HEIGHT_RATIO * zoom_level)
        vertical_offset = self.tile_size * VERTICAL_OFFSET_RATIO * zoom_level
        border_thickness = max(1, int(zoom_level))
        
        # Calcul de la position
        bar_x = x - HORIZONTAL_OFFSET + (self.tile_size * zoom_level - bar_width) / 8
        bar_y = y - 3 * vertical_offset
        
        # Couleurs
        BORDER_COLOR = (0, 20, 0)
        BACKGROUND_COLOR = (200, 0, 0)
        HEALTH_COLOR = (0, 190, 0)
        
        # Dimensions des rectangles
        border_rect = (
            bar_x - border_thickness,
            bar_y - border_thickness,
            bar_width + 2 * border_thickness,
            bar_height + 2 * border_thickness
        )
        
        base_rect = (bar_x, bar_y, bar_width, bar_height)
        
        # Dessin des différentes couches
        pygame.draw.rect(surface, BORDER_COLOR, border_rect)  # Contour
        pygame.draw.rect(surface, BACKGROUND_COLOR, base_rect)  # Fond rouge
        
        # Barre de vie verte
        if unit.health > 0:
            health_width = bar_width * (unit.health / unit.max_health)
            health_rect = (bar_x, bar_y, health_width, bar_height)
            pygame.draw.rect(surface, HEALTH_COLOR, health_rect)

    def draw_unit(self, surface, unit, x, y, zoom_level=1.0):
        # ...existing code...
        self.draw_health_bar(surface, unit, x, y, zoom_level)

    def render_resources(self):
        """
        Affiche le panneau de ressources pour les deux joueurs avec leurs ressources actuelles.
        Inclut le nom du joueur et les icônes/quantités de ressources.
        """
        # Constantes de style et de positionnement
        PANEL_POSITIONS = {
            1: 10,   # y position pour joueur 1
            2: 100   # y position pour joueur 2
        }

        # Rendu principal pour les deux joueurs
        for player_id, panel_y in PANEL_POSITIONS.items():
            self.render_player_panel(player_id, panel_y)
            
    def render_resource_icons(self, resources, base_y):
        """Sous-fonction pour rendre les icônes et quantités de ressources."""
        
        TEXT_COLOR = (255, 255, 255)
        RESOURCE_START_X = 40
        RESOURCE_Y_OFFSET = 25  
        
        for i, (resource_type, amount) in enumerate(resources.items()):
            resource_key = resource_type.lower()
            x_pos = self.panel_x + RESOURCE_START_X + (i * self.spacing)
            y_pos = base_y + RESOURCE_Y_OFFSET

            # Icône de la ressource
            self.screen.blit(
                self.resource_icons[resource_key],
                (x_pos, y_pos)
            )

            # Quantité de la ressource
            amount_text = self.font.render(str(amount), True, TEXT_COLOR)
            amount_pos = (
                x_pos + self.resource_text_offsets[resource_key],
                y_pos + 8
            )
            self.screen.blit(amount_text, amount_pos)

    def render_player_panel(self, player_id, panel_y):
        """Sous-fonction pour rendre le panneau d'un joueur spécifique."""
        
        PLAYER_COLORS = {
            1: (255, 215, 0),    # Or pour joueur 1
            2: (0, 191, 255)     # Bleu pour joueur 2
        }
        
        PLAYER_NAME_OFFSET_X = 10
        PLAYER_NAME_OFFSET_Y = 5
        
        # Fond du panneau
        self.screen.blit(self.scaled_panel, (self.panel_x, panel_y))

        # Nom du joueur
        player_text = self.font.render(
            f"Player {player_id}",
            True,
            PLAYER_COLORS[player_id]
        )
        player_text_pos = (
            self.panel_x + PLAYER_NAME_OFFSET_X,
            panel_y + PLAYER_NAME_OFFSET_Y
        )
        self.screen.blit(player_text, player_text_pos)

        # Rendu des ressources
        resources = self.game_state.player_resources[player_id]
        self.render_resource_icons(resources, panel_y)