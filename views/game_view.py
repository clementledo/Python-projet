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

    def render(self, model, camera_x, camera_y, zoom_level):
        """Render game state"""
        self.screen.fill((0, 0, 0))
        
        # Render map
        self.render_map(model['map'], camera_x, camera_y, zoom_level)
        
        # Render buildings
        self.render_buildings(model['buildings'], camera_x, camera_y, zoom_level)
        
        # Render units
        self.render_units(model['units'], camera_x, camera_y, zoom_level)
        
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
        minimap_width = 650  # Anciennement 400
        minimap_height = 220  # Anciennement 200
        minimap_x = self.screen.get_width() - minimap_width - 10 + 5  # Ajout de 5 pixels à droite
        minimap_y = self.screen.get_height() - minimap_height - 10 + 5  # Ajout de 5 pixels en bas

        # Couleurs des terrains
        terrain_colors = {
            Terrain_type.GRASS: (34, 139, 34),  # Vert pour l'herbe
            Terrain_type.WATER: (65, 105, 225),  # Bleu pour l'eau
        }

        # Surface de la minimap
        minimap_surface = pygame.Surface((minimap_width, minimap_height))
        minimap_surface.fill((50, 50, 50))  # Fond sombre

        # Calcul dynamique pour que les cases remplissent la minimap
        tile_width = minimap_width / (map_data.largeur + map_data.hauteur) * 2
        tile_width = int(tile_width)
        tile_height = tile_width // 2

        # Décalages pour bien centrer
        offset_x = minimap_width // 2
        offset_y = minimap_height // 2 - (map_data.hauteur * tile_height) // 2

        for y in range(map_data.hauteur):
            for x in range(map_data.largeur):
                tile = map_data.grille[y][x]
                if tile:
                    color = terrain_colors.get(tile.terrain_type, (100, 100, 100))
                    iso_x = (x - y) * tile_width // 2
                    iso_y = (x + y) * tile_height // 2
                    iso_x += offset_x
                    iso_y += offset_y
                    diamond_points = [
                        (iso_x, iso_y),
                        (iso_x + tile_width // 2, iso_y + tile_height // 2),
                        (iso_x, iso_y + tile_height),
                        (iso_x - tile_width // 2, iso_y + tile_height // 2),
                    ]
                    pygame.draw.polygon(minimap_surface, color, diamond_points)

        # Rendu des unités en iso
        for unit in units:
            ux, uy = unit.get_position()
            iso_ux = (ux - uy) * tile_width // 2 + offset_x
            iso_uy = (ux + uy) * tile_height // 2 + offset_y
            unit_color = {
                'villager': (255, 0, 0),
                'archer': (0, 0, 255),
            }.get(unit.unit_type, (255, 255, 255))
            pygame.draw.circle(minimap_surface, unit_color, (int(iso_ux), int(iso_uy)), 2)

        # Rendu des bâtiments en iso
        for building in buildings:
            bx, by = building.pos
            iso_bx = (bx - by) * tile_width // 2 + offset_x
            iso_by = (bx + by) * tile_height // 2 + offset_y
            pygame.draw.rect(minimap_surface, (255, 0, 0),
                             (iso_bx - 2, iso_by - 2, 4, 4))

        # Afficher la minimap sur l'écran
        self.screen.blit(minimap_surface, (minimap_x, minimap_y))

        # Bordure de la minimap
        pygame.draw.rect(
            self.screen,
            (100, 100, 100),
            (minimap_x, minimap_y, minimap_width, minimap_height),
            5  # Anciennement 4
    )
        
    
        


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

                    # Position interpolation for smooth movement
                    if not hasattr(unit, "display_position"):
                        unit.display_position = unit.get_position()  # Initialize display position

                    x_target, y_target = unit.get_position()
                    x_display, y_display = unit.display_position

                    # Interpolation speed
                    move_speed = 0.1  # Adjust this value for faster/slower interpolation

                    # Linear interpolation towards target position
                    x_display += (x_target - x_display) * move_speed
                    y_display += (y_target - y_display) * move_speed

                    # Update the display position
                    unit.display_position = (x_display, y_display)

                    iso_x, iso_y = self.world_to_screen(x_display, y_display, camera_x, camera_y, zoom_level)
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


