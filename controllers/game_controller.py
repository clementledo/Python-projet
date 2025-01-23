import pygame
import math
from models.Buildings.town_center import Town_center  # Adjust the import path as necessary

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
        self.zoom_level = 0.5
        self.selected_unit = None
        self.selected_building = None
        self.player_resources = {}

        self.paused = False

        self.clock = pygame.time.Clock()
         # Gérer le clic et le déplacement de la souris
        self.is_dragging = False
        self.last_mouse_pos = None

        self.screen_width, self.screen_height = view.screen.get_size()
        self.map_pixel_width = carte.largeur * view.tile_size * 2
        self.map_pixel_height = carte.hauteur * view.tile_size * 2
        self.camera_boundary_x = max(0, self.map_pixel_width - self.screen_width)
        self.camera_boundary_y = max(0, self.map_pixel_height - self.screen_height)
        self.selected_units = []  # List of currently selected units

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            # Left click for selection
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                clicked_unit = self.get_unit_at_position(mouse_pos)
                clicked_building = self.get_building_at_position(mouse_pos)
                
                # If we clicked a unit
                if clicked_unit:
                    self.handle_unit_selection(clicked_unit)
                    # If we already had a building selected, move to it
                    if self.selected_building:
                        self.move_units_to_building(self.selected_building)
                        self.selected_building = None
                
                # If we clicked a building
                elif clicked_building:
                    self.selected_building = clicked_building
                    # If we already had units selected, move them
                    if self.selected_units:
                        self.move_units_to_building(clicked_building)
                        self.selected_building = None
                
                # Clicked nothing - clear selections
                else:
                    self.selected_units = []
                    self.selected_building = None

            # Right click for movement command
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                mouse_pos = pygame.mouse.get_pos()
                clicked_building = self.get_building_at_position(mouse_pos)
                
                if clicked_building and isinstance(clicked_building, Town_center):
                    if self.selected_units:  # If units are selected
                        for unit in self.selected_units:
                            unit.move_towards(clicked_building.pos, self.carte)
                        print(f"Moving {len(self.selected_units)} units to Town Center")
            
            if event.type == pygame.KEYDOWN:
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
                
                # Gestion des clics sur la minimap
                self.handle_minimap_click(self.last_mouse_pos)

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

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Select units
                    mouse_pos = pygame.mouse.get_pos()
                    clicked_unit = self.get_unit_at_position(mouse_pos)
                    if clicked_unit:
                        if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                            self.selected_units.append(clicked_unit)
                        else:
                            self.selected_units = [clicked_unit]
                    else:
                        self.selected_units = []

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
    
    
    def handle_minimap_click(self, mouse_pos):
        """Gère les clics sur la minimap pour déplacer la caméra."""
        
        minimap_width = 200
        minimap_height = 200
        minimap_x = self.view.screen.get_width() - minimap_width - 10
        minimap_y = self.view.screen.get_height() - minimap_height - 10
        minimap_rect = pygame.Rect(minimap_x, minimap_y, minimap_width, minimap_height)

        # Vérifier si le clic est dans la minimap
        if minimap_rect.collidepoint(mouse_pos):
        # Calculer les coordonnées relatives du clic dans la minimap
            rel_x = mouse_pos[0] - minimap_rect.x
            rel_y = mouse_pos[1] - minimap_rect.y
            
            

            # Convertir les coordonnées relatives en coordonnées de la carte
            map_x = int((rel_x / minimap_rect.width) * (self.map_width * self.tile_size))
            map_y = int((rel_y / minimap_rect.height) * (self.map_height * self.tile_size))

            # Ajuster la caméra pour centrer sur la position cliquée
            self.camera_x = max(0, min(self.camera_boundary_x, map_x - self.screen_width // (2 * self.zoom_level)))
            self.camera_y = max(0, min(self.camera_boundary_y, map_y - self.screen_height // (2 * self.zoom_level)))

            print(f"Camera moved to ({self.camera_x}, {self.camera_y}) via minimap click.")

    

    def validate_positions(self):
        # Clamp units
        for unit in self.model['units']:
            x, y = unit.get_position()
            unit.x_tile = max(0, min(x, self.carte.largeur - 1))
            unit.y_tile = max(0, min(y, self.carte.hauteur - 1))
        
        # Clamp buildings
        for building in self.model['buildings']:
            building.update()
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

    def move_unit_to_town_center(self):
        """Move selected units to town center."""
        # Find town center
        town_center = None
        for building in self.model['buildings']:
            if isinstance(building, Town_center):
                town_center = building
                break
        
        if town_center:
            # Move all selected units or first unit if none selected
            if self.selected_units:
                for unit in self.selected_units:
                    unit.move_to(town_center.pos, self.carte)
            elif self.model['units']:
                self.model['units'][3].move_towards(town_center.pos, self.carte)

    def get_unit_at_position(self, screen_pos):
        """Get unit at screen position."""
        world_x = (screen_pos[0] + self.camera_x) / (self.view.tile_size * self.zoom_level)
        world_y = (screen_pos[1] + self.camera_y) / (self.view.tile_size * self.zoom_level)
        
        for unit in self.model['units']:
            unit_x, unit_y = unit.position
            # Check if click is within unit bounds
            if (abs(unit_x - world_x) < 1 and 
                abs(unit_y - world_y) < 1):
                return unit
        return None

    def get_building_at_position(self, screen_pos):
        """Get building at screen position."""
        world_x = (screen_pos[0] + self.camera_x) / (self.view.tile_size * self.zoom_level)
        world_y = (screen_pos[1] + self.camera_y) / (self.view.tile_size * self.zoom_level)
        
        for building in self.model['buildings']:
            building_x, building_y = building.pos
            building_size = building.size
            if (building_x <= world_x < building_x + building_size[0] and 
                building_y <= world_y < building_y + building_size[1]):
                return building
        return None

    def move_selected_units_to_town_center(self):
        """Move selected units to town center."""
        if not self.selected_units:
            return
            
        # Find town center
        town_center = None
        for building in self.model['buildings']:
            if isinstance(building, Town_center):
                town_center = building
                break
        
        if town_center:
            for unit in self.selected_units:
                unit.move_towards(town_center.pos, self.carte)
            print(f"Moving {len(self.selected_units)} units to Town Center")

    def handle_unit_selection(self, unit):
        if pygame.key.get_mods() & pygame.KMOD_SHIFT:
            if unit not in self.selected_units:
                self.selected_units.append(unit)
        else:
            self.selected_units = [unit]
        print(f"Selected units: {[u.unit_type for u in self.selected_units]}")

    def move_units_to_building(self, building):
        if not self.selected_units:
            return
        for unit in self.selected_units:
            unit.move_towards(building.pos, self.carte)
        print(f"Moving {len(self.selected_units)} units to building at {building.pos}")

    

    def render_resources(self):
        """Render resource display"""
        self.view.render_resource_panel()