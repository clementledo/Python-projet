import pygame
from models.Resources.Terrain_type import Terrain_type
import random
import math
from models.units.villager import Villager

class GameView:
    def __init__(self, screen, tile_size=50):
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
        
        # Précharger et mettre en cache les textures de terrain
        self.terrain_textures = {}
        self._initialize_terrain_textures()

        # Ajout des attributs pour la mini carte
        self.minimap_surface = None
        self.minimap_update_counter = 0
        self.minimap_update_frequency = 30  # Met à jour tous les 30 frames
        self.cached_minimap = None
        self.last_minimap_state = None

    def _initialize_terrain_textures(self):
        """Précharge toutes les textures de terrain une seule fois"""
        base_textures = {
            Terrain_type.GRASS: pygame.image.load('assets/t_grass.png').convert_alpha(),
            Terrain_type.WATER: pygame.image.load('assets/t_water.png').convert_alpha(),
        }
        
        # Créer des versions 5x5 des textures
        for terrain, texture in base_textures.items():
            scaled = pygame.transform.scale(texture, 
                (self.tile_size * 10, self.tile_size * 5))  # 5x5 tiles
            self.terrain_textures[terrain] = scaled

    def render(self, model, camera_x, camera_y, zoom_level):
        """Render game state"""
        self.screen.fill((0, 0, 0))
        
        # Render map
        self.render_map(model['map'], camera_x, camera_y, zoom_level)
        
        # Render buildings
        self.render_buildings(model['buildings'], camera_x, camera_y, zoom_level)
        
        # Render units
        self.render_units(model['units'], camera_x, camera_y, zoom_level)
        
        # Render minimap
        self.render_minimap(model['map'], camera_x, camera_y, zoom_level, model['units'], model['buildings'])  # Appel de la mini carte
        
        # Update display
        pygame.display.flip()
    
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
        """Rendu optimisé de la carte avec regroupement des tuiles en blocs 5x5."""
        screen_width, screen_height = self.screen.get_size()
        map_width = len(carte.grille[0])
        map_height = len(carte.grille)

        # Calculer les dimensions de tuile actuelles avec le zoom
        tile_width = int(self.tile_size * 2 * zoom_level)
        tile_height = int(self.tile_size * zoom_level)

        # Redimensionner les textures pour le zoom actuel (une seule fois par bloc)
        zoomed_textures = {}
        for terrain, texture in self.terrain_textures.items():
            zoomed_textures[terrain] = pygame.transform.scale(texture, 
                (tile_width * 5, tile_height * 5))

        # Parcourir la carte par blocs de 5x5
        for base_y in range(0, map_height, 5):
            for base_x in range(0, map_width, 5):
                # Vérifier le type de terrain dominant dans le bloc 5x5
                terrain_counts = {Terrain_type.GRASS: 0, Terrain_type.WATER: 0}
                
                for y in range(base_y, min(base_y + 5, map_height)):
                    for x in range(base_x, min(base_x + 5, map_width)):
                        if 0 <= x < map_width and 0 <= y < map_height:
                            tile = carte.grille[y][x]
                            if tile:
                                terrain_counts[tile.terrain_type] = \
                                    terrain_counts.get(tile.terrain_type, 0) + 1

                # Déterminer le type de terrain dominant
                dominant_terrain = max(terrain_counts.items(), key=lambda x: x[1])[0]
                
                # Calculer la position du bloc
                iso_x, iso_y = self.world_to_screen(base_x, base_y, camera_x, camera_y, zoom_level)
                iso_x += screen_width // 2
                iso_y += screen_height // 4

                # Dessiner le bloc de terrain
                self.screen.blit(zoomed_textures[dominant_terrain], (iso_x, iso_y))

        # Dessiner les lignes de grille principales (tous les 5 tiles)
        for y in range(0, map_height, 5):
            for x in range(0, map_width, 5):
                grid_x, grid_y = self.world_to_screen(x, y, camera_x, camera_y, zoom_level)
                grid_x += screen_width // 2
                grid_y += screen_height // 4
                
                points = [
                    (grid_x, grid_y + tile_height*2.5),
                    (grid_x + tile_width*2.5, grid_y),
                    (grid_x + tile_width*5, grid_y + tile_height*2.5),
                    (grid_x + tile_width*2.5, grid_y + tile_height*5),
                    (grid_x, grid_y + tile_height*2.5)
                ]
                pygame.draw.lines(self.screen, (100, 100, 100), True, points, 2)

        # Render decorations
        self.render_decorations(carte, camera_x, camera_y, zoom_level)

    def render_decorations(self, carte, camera_x, camera_y, zoom_level):
        """Méthode séparée pour le rendu des décorations."""
        screen_width, screen_height = self.screen.get_size()
        tile_width = int(self.tile_size * 2 * zoom_level)
        tile_height = int(self.tile_size * zoom_level)

        for decoration in self.decorations:
            x, y = decoration['x'], decoration['y']
            if not (0 <= x < carte.largeur and 0 <= y < carte.hauteur):
                continue

            iso_x, iso_y = self.world_to_screen(x, y, camera_x, camera_y, zoom_level)
            iso_x += screen_width // 2
            iso_y += screen_height // 4 - tile_height

            decoration_image = pygame.transform.scale(
                decoration['image'], 
                (tile_width, tile_height * 2)
            )
            self.screen.blit(decoration_image, (iso_x, iso_y))

    def render_minimap(self, map_data, camera_x, camera_y, zoom_level, units, buildings):
        """Version optimisée de la mini carte avec mise en cache."""
        # Dimensions de la mini carte
        minimap_width = 400
        minimap_height = 400
        background_height = 200
        padding_x = 10
        padding_y = -185
        screen_width, screen_height = self.screen.get_size()
        minimap_x = screen_width - minimap_width - padding_x
        minimap_y = screen_height - minimap_height - padding_y

        # Vérifier si une mise à jour est nécessaire
        current_state = (len(units), len(buildings), camera_x, camera_y)
        force_update = self.cached_minimap is None or self.last_minimap_state != current_state
        
        # Mettre à jour la mini carte périodiquement ou si forcé
        if self.minimap_update_counter >= self.minimap_update_frequency or force_update:
            if self.cached_minimap is None:
                self.cached_minimap = pygame.Surface((minimap_width, minimap_height), pygame.SRCALPHA)
            
            self.cached_minimap.fill((0, 0, 0, 0))
            
            # Dessiner le fond
            pygame.draw.rect(
                self.cached_minimap,
                (50, 50, 50, 200),
                (0, 0, minimap_width, background_height)
            )

            # Paramètres isométriques simplifiés
            base_tile_w = 8
            base_tile_h = 4

            # Calcul des limites une seule fois
            min_ix, max_ix, min_iy, max_iy = self._calculate_minimap_bounds(map_data, base_tile_w, base_tile_h)
            
            # Calcul de l'échelle
            iso_width = max_ix - min_ix + 1
            iso_height = max_iy - min_iy + 1
            scale = min(minimap_width / iso_width, minimap_height / iso_height) if iso_width and iso_height else 1

            # Fonction de transformation optimisée
            def iso_transform(x, y):
                ix = (x - y) * base_tile_w // 2
                iy = (x + y) * base_tile_h // 2
                return (int((ix - min_ix) * scale), int((iy - min_iy) * scale))

            # Dessiner le terrain (optimisé)
            self._draw_minimap_terrain(map_data, iso_transform, self.cached_minimap)
            
            # Dessiner les unités et bâtiments (optimisé)
            self._draw_minimap_entities(units, buildings, iso_transform, self.cached_minimap)

            self.minimap_update_counter = 0
            self.last_minimap_state = current_state
        else:
            self.minimap_update_counter += 1

        # Afficher la mini carte mise en cache
        self.screen.blit(self.cached_minimap, (minimap_x, minimap_y))

    def _calculate_minimap_bounds(self, map_data, base_tile_w, base_tile_h):
        """Calcule les limites de la mini carte."""
        min_ix = float('inf')
        max_ix = -float('inf')
        min_iy = float('inf')
        max_iy = -float('inf')

        for y in range(0, map_data.hauteur, 2):  # Optimisé: échantillonnage
            for x in range(0, map_data.largeur, 2):
                ix = (x - y) * base_tile_w // 2
                iy = (x + y) * base_tile_h // 2
                min_ix = min(min_ix, ix)
                max_ix = max(max_ix, ix)
                min_iy = min(min_iy, iy)
                max_iy = max(max_iy, iy)

        return min_ix, max_ix, min_iy, max_iy

    def _draw_minimap_terrain(self, map_data, transform_func, surface):
        """Dessine le terrain sur la mini carte de manière simplifiée."""
        for y in range(map_data.hauteur):
            for x in range(map_data.largeur):
                if not (0 <= x < map_data.largeur and 0 <= y < map_data.hauteur):
                    continue
                    
                tile = map_data.grille[y][x]
                if not tile:
                    continue

                iso_x, iso_y = transform_func(x, y)
                color = (34, 139, 34) if tile.terrain_type == Terrain_type.GRASS else (0, 191, 255)
                # Simplement dessiner le rectangle sans bordure
                pygame.draw.rect(surface, color, (iso_x, iso_y, 2, 2))

    def _draw_minimap_entities(self, units, buildings, transform_func, surface):
        """Dessine les unités et bâtiments sur la mini carte."""
        # Dessiner les bâtiments
        for b in buildings:
            iso_x, iso_y = transform_func(b.pos[0], b.pos[1])
            pygame.draw.rect(surface, (255, 0, 0), (iso_x, iso_y, 4, 4))

        # Dessiner les unités
        for u in units:
            x, y = u.get_position()
            iso_x, iso_y = transform_func(x, y)
            pygame.draw.circle(surface, (0, 255, 0), (iso_x, iso_y), 2)

    def colorize_surface(self, surface, color):
        """Apply color tint to a surface"""
        colorized = surface.copy()
        colorized.fill(color, special_flags=pygame.BLEND_RGBA_MULT)
        return colorized

    def render_unit_paths(self, units, camera_x, camera_y, zoom_level):
        """Render paths for units that are moving"""
        for unit in units:
            path = unit.get_path_for_rendering()
            if path:
                # Convert path points to screen coordinates
                screen_points = []
                for point in path:
                    iso_x, iso_y = self.world_to_screen(point[0], point[1], camera_x, camera_y, zoom_level)
                    iso_x += self.screen.get_width() // 2
                    iso_y += self.screen.get_height() // 4
                    screen_points.append((int(iso_x), int(iso_y)))
                
                if len(screen_points) > 1:
                    pygame.draw.lines(self.screen, (205, 55, 0), False, screen_points, 1)

    def render_units(self, units, camera_x, camera_y, zoom_level, selected_unit=None):
        # Draw paths first
        self.render_unit_paths(units, camera_x, camera_y, zoom_level)
        for unit in units:
            if isinstance(unit, Villager):
                sprite = unit.get_current_sprite()
                if sprite:
                    tile_width = int(self.tile_size * 2 * zoom_level)
                    tile_height = int(self.tile_size * zoom_level)
                    screen_width, screen_height = self.screen.get_size()

                    x_tile, y_tile = unit.get_position()
                    iso_x, iso_y = self.world_to_screen(x_tile, y_tile, camera_x, camera_y, zoom_level)
                    
                    iso_x += screen_width // 2
                    iso_y += screen_height // 4

                    if selected_unit == unit:
                        highlight_color = (255, 255, 0)
                        highlight_radius = int(tile_width * 0.5)
                        pygame.draw.circle(self.screen, highlight_color, 
                                        (iso_x, iso_y + tile_height // 2), highlight_radius, 2)

                    scaled_sprite = pygame.transform.scale(sprite, 
                        (int(sprite.get_width() * zoom_level), 
                        int(sprite.get_height() * zoom_level)))
                    
                    # Apply blue tint for Player 2 units
                    if unit.player_id == 2:
                        scaled_sprite = self.colorize_surface(scaled_sprite, (100, 100, 255, 255))
                    
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
        """Render buildings with foundations"""
        screen_width, screen_height = self.screen.get_size()
        mouse_pos = pygame.mouse.get_pos()
        
        for building in buildings:
            building_x, building_y = building.pos
            iso_x, iso_y = self.world_to_screen(building_x, building_y, camera_x, camera_y, zoom_level)
            
            iso_x += screen_width // 2
            iso_y += screen_height // 4
            
            sprite = self.building_sprites.get(building.symbol)
            if sprite:
                # Scale sprite first to check bounds
                scaled_sprite = pygame.transform.scale(sprite, 
                    (int(sprite.get_width() * zoom_level), 
                     int(sprite.get_height() * zoom_level)))
                
                # Calculate sprite bounds for mouse detection
                sprite_rect = pygame.Rect(
                    iso_x - scaled_sprite.get_width() // 2,
                    iso_y - scaled_sprite.get_height() // 2,
                    scaled_sprite.get_width(),
                    scaled_sprite.get_height()
                )
                
                # Only draw foundation if mouse is over building
                if sprite_rect.collidepoint(mouse_pos):
                    # Calculate foundation size
                    tile_width = self.tile_size * zoom_level
                    tile_height = tile_width / 2
                    
                    foundation_width = building.size[0] * tile_width 
                    foundation_height = building.size[1] * tile_height 
                    
                    foundation_points = [
                        (iso_x, iso_y + foundation_height),
                        (iso_x - foundation_width, iso_y),
                        (iso_x, iso_y - foundation_height),
                        (iso_x + foundation_width, iso_y),
                        (iso_x, iso_y + foundation_height)
                    ]
                    
                    pygame.draw.lines(self.screen, (255, 255, 255), False, foundation_points, 1)
                
                # Draw building sprite
                if building.player_id == 2:
                    scaled_sprite = self.colorize_surface(scaled_sprite, (100, 100, 255, 255))
                
                self.screen.blit(scaled_sprite, 
                    (iso_x - scaled_sprite.get_width() // 2, 
                     iso_y - scaled_sprite.get_height() // 2))

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
        """Display resource panel with current resources for both players"""
        # Panel dimensions
        panel_width = 700
        panel_height = 80
        padding = 10

        # Panel positions
        panel1_x = 1220
        panel1_y = 10
        panel2_x = 1220
        panel2_y = 100  # Below player 1's panel

        # Resource icon size and spacing
        icon_size = 40
        spacing = 150

        # Draw panels for both players
        for player_id, panel_y in [(1, panel1_y), (2, panel2_y)]:
            # Draw panel background
            scaled_panel = pygame.transform.scale(self.resource_panel, (panel_width, panel_height))
            self.screen.blit(scaled_panel, (panel1_x, panel_y))

            # Player label
            player_text = self.font.render(f"Player {player_id}", True, 
                                         (255, 215, 0) if player_id == 1 else (0, 191, 255))
            self.screen.blit(player_text, (panel1_x + 10, panel_y + 5))

            # Display each resource
            resources_to_display = self.game_state.player_resources[player_id]
            for i, (resource_type, amount) in enumerate(resources_to_display.items()):
                # Position for this resource
                x = panel1_x + 40 + (i * spacing)
                y = panel_y + 25
                
                # Draw icon
                resource_type = resource_type.lower()
                icon = pygame.transform.scale(self.resource_icons[resource_type], (icon_size, icon_size))
                self.screen.blit(icon, (x, y))
                
                # Draw amount
                text = self.font.render(str(amount), True, (255, 255, 255))
                self.screen.blit(text, (x + icon_size + 20, y + 8))
    def render_game(self, game_state, screen, clock, font):
        """Render the entire game state."""
        controller = game_state.controller
        view = game_state.view
        
        screen.fill((0, 0, 0))
        
        self.render_map(game_state.carte, controller.camera_x, controller.camera_y, controller.zoom_level)
        self.generate_resources(game_state.carte)
        self.render_units(game_state.model['units'], controller.camera_x, controller.camera_y, 
                         controller.zoom_level, controller.selected_unit)
        self.render_buildings(game_state.model['buildings'], controller.camera_x, controller.camera_y, 
                             controller.zoom_level)
        self.render_minimap(game_state.carte, controller.camera_x, controller.camera_y,
                           controller.zoom_level, game_state.model['units'], game_state.model['buildings'])
        
        game_state.show_fps(clock=clock, font=font, screen=screen)
        pygame.display.flip()


