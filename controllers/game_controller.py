import pygame
import math

class GameController:
    def __init__(self, model, view, carte,tile_size):
        # ... (existing initialization) ...
        self.tile_size = tile_size
        self.model = model
        self.view = view
        self.carte = carte
        self.selected_unit = None  # Unité sélectionnée par le joueur
        self.camera_x = 0  # Position X de la caméra
        self.camera_y = 0  # Position Y de la caméra
        self.camera_speed = 10  # Vitesse de déplacement de la caméra
        self.selected_unit = None
        self.map_width = carte.largeur
        self.map_height = carte.hauteur
        self.zoom_level = 1.5
        self.selected_unit = None
        self.selected_building = None

        self.paused = False

        self.clock = pygame.time.Clock()
         # Gérer le clic et le déplacement de la souris
        self.is_dragging = False
        self.last_mouse_pos = None

        self.screen_width, self.screen_height = view.screen.get_size()
        self.map_pixel_width = carte.largeur * view.tile_size * 2
        self.map_pixel_height = carte.hauteur * view.tile_size
        self.camera_boundary_x = max(0, self.map_pixel_width - self.screen_width)
        self.camera_boundary_y = max(0, self.map_pixel_height - self.screen_height)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type ==pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # Basculer entre pause et reprise avec 'Échap'
                    self.paused = not self.paused
                    print(f"Game paused: {self.paused}")

            # Zoom handling
            if event.type == pygame.MOUSEWHEEL:
                self.zoom_level = max(0.5, min(2.0, self.zoom_level + event.y * 0.1))

            # Camera dragging
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.is_dragging = False
                self.last_mouse_pos = pygame.mouse.get_pos()

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.is_dragging = False
                self.last_mouse_pos = None
                
                # Check for unit selection
                self.select_unit(pygame.mouse.get_pos())


                # Gestion des clics sur les bâtiments
                self.select_building(pygame.mouse.get_pos())

                 # Sélection d'un bâtiment
                mouse_pos = pygame.mouse.get_pos()
                map_x = int(mouse_pos[0] / (self.tile_size * self.zoom_level) + self.camera_x)
                map_y = int(mouse_pos[1] / (self.tile_size * self.zoom_level) + self.camera_y)
                
                for building in self.model['buildings']:
                    bx, by = building.pos
                    if bx == map_x and by == map_y:
                        self.selected_building = building
                        print(f"Building selected at {map_x}, {map_y}")
                        break

            if event.type == pygame.MOUSEMOTION and self.is_dragging:
                current_mouse_pos = pygame.mouse.get_pos()
                if self.last_mouse_pos:
                    dx = current_mouse_pos[0] - self.last_mouse_pos[0]
                    dy = current_mouse_pos[1] - self.last_mouse_pos[1]

                    # Update camera position with boundaries
                    self.camera_x = max(0, min(self.camera_boundary_x, self.camera_x - dx))
                    self.camera_y = max(0, min(self.camera_boundary_y, self.camera_y - dy))

                    self.last_mouse_pos = current_mouse_pos

        self.validate_positions()
        
        # Déplacement de la caméra avec les touches de direction
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.camera_x -= self.camera_speed
        if keys[pygame.K_RIGHT]:
            self.camera_x += self.camera_speed
        if keys[pygame.K_UP]:
            self.camera_y -= self.camera_speed
        if keys[pygame.K_DOWN]:
            self.camera_y += self.camera_speed
       


        return True
    

    def validate_positions(self):
        # Clamp units
        for unit in self.model['units']:
            x, y = unit.get_position()
            unit.x_tile = max(0, min(x, self.carte.largeur - 1))
            unit.y_tile = max(0, min(y, self.carte.hauteur - 1))
        
        # Clamp buildings
        for building in self.model['buildings']:
            x, y = building.pos
            width, height = building.size
            clamped_x = max(0, min(x, self.carte.largeur - 1))
            clamped_y = max(0, min(y, self.carte.hauteur - 1))
            building.pos = (clamped_x, clamped_y)


    def select_unit(self, mouse_pos):
        """Improved unit selection with screen-to-world conversion"""
        screen_width, screen_height = self.view.screen.get_size()
        
        for unit in self.model['units']:
            # Get unit's screen position
            x_tile, y_tile = unit.get_position()
            iso_x, iso_y = self.view.world_to_screen(x_tile, y_tile, 
                                                     self.camera_x, 
                                                     self.camera_y, 
                                                     self.zoom_level)
            
            # Center the map
            iso_x += screen_width // 2
            iso_y += screen_height // 4

            # Check if mouse is near the unit
            unit_rect = pygame.Rect(
                iso_x - 20, 
                iso_y - 20, 
                40, 
                40
            )
            
            if unit_rect.collidepoint(mouse_pos):
                self.selected_unit = unit
                print(f"Selected unit {unit.unit_type} at {x_tile}, {y_tile}")
                return
        
        print("No unit selected")

    def select_building(self, mouse_pos):
        """Sélectionne un bâtiment en fonction des coordonnées de la souris, avec projection isométrique."""
        screen_width, screen_height = self.view.screen.get_size()

        for building in self.model['buildings']:
            building_x, building_y = building.pos
            
            # Convertir la position du bâtiment en coordonnées écran avec la projection isométrique
            iso_x, iso_y = self.view.world_to_screen(building_x, building_y, 
                                                    self.camera_x, self.camera_y, 
                                                    self.zoom_level)
            
            # Centrer la vue pour la position isométrique
            iso_x += screen_width // 2
            iso_y += screen_height // 4

            # Calculer les coordonnées de la zone occupée par le bâtiment (en tenant compte de la taille)
            building_width = int(self.tile_size * building.size[0] * self.zoom_level)
            building_height = int(self.tile_size * building.size[1] * self.zoom_level)
            
            # Créer un rectangle de collision autour du bâtiment
            building_rect = pygame.Rect(
                iso_x - building_width // 2,  # Centrer horizontalement
                iso_y - building_height // 2,  # Centrer verticalement
                building_width, 
                building_height
            )

            # Vérifier si la souris est à l'intérieur de ce rectangle
            if building_rect.collidepoint(mouse_pos):
                self.selected_building = building
                print(f"Building selected at {building.pos} with size {building.size}")
                return

        self.selected_building = None
        print("No building selected.")


    def update(self):
        # ... autres mises à jour ...
        self.view.render_units(self.model['units'], self.camera_x, self.camera_y, self.zoom_level, self.selected_unit)