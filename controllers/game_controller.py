import pygame
from models.units.unit import Unit
from models.map import Map
from views.game_view import GameView

class GameController:
    def __init__(self, model, view, carte):
        self.model = model
        self.view = view
        self.carte = carte
        self.selected_unit = None  # Unité sélectionnée par le joueur
        self.camera_x = 0 # Position X de la caméra
        self.camera_y = 0 # Position y de la caméra
        self.camera_speed = 5 # Vitesse de déplacement de la caméra
        self.selected_unit = None
        self.map_width = carte.largeur
        self.map_height = carte.hauteur
        self.zoom_level = 1.0


        # Gérer le clic et le déplacement de la souris
        self.is_dragging = False
        self.last_mouse_pos = None



    def handle_input(self):
        """Gère les événements clavier/souris pour le déplacement de la carte seulement."""

        # Accéder à la largeur et hauteur de l'écran via la vue
        screen_width = self.view.screen.get_width()
        screen_height = self.view.screen.get_height()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False  # Quitter la boucle de jeu

            # Gestion du zoom avec la molette de la souris
            if event.type == pygame.MOUSEWHEEL:
                if event.y > 0:  # Molette vers le haut : zoom avant
                    self.zoom_level = min(self.zoom_level + 0.1, 2.0)  # Limite maximale du zoom
                else:  # Molette vers le bas : zoom arrière
                    self.zoom_level = max(self.zoom_level - 0.1, 0.5)  # Limite minimale du zoom    

            # Début du clic gauche (déplacement de la caméra)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Clic gauche
                mouse_pos = pygame.mouse.get_pos()
                self.is_dragging = True
                self.last_mouse_pos = mouse_pos

            # Fin du clic gauche
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:  # Relâchement du clic gauche
                self.is_dragging = False
                self.last_mouse_pos = None

            # Déplacement de la souris pendant que le clic gauche est maintenu
            if event.type == pygame.MOUSEMOTION and self.is_dragging:
                current_mouse_pos = pygame.mouse.get_pos()
                if self.last_mouse_pos:
                    # Calculer le déplacement de la souris
                    dx = current_mouse_pos[0] - self.last_mouse_pos[0]
                    dy = current_mouse_pos[1] - self.last_mouse_pos[1]
                    
                    # Déplacer la caméra en fonction du mouvement de la souris
                    self.camera_x -= dx
                    self.camera_y -= dy
                    
                    # Limiter la caméra pour qu'elle ne dépasse pas les bords de la carte
                    map_pixel_width = self.map_width * self.view.tile_size * 2
                    map_pixel_height = self.map_height * self.view.tile_size

                    self.camera_x = max(0, min(self.camera_x, map_pixel_width - screen_width))
                    self.camera_y = max(0, min(self.camera_y, map_pixel_height - screen_height))
                
                # Mettre à jour la dernière position de la souris
                self.last_mouse_pos = current_mouse_pos

        # Gestion des touches de direction pour déplacer la caméra
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_RIGHT]:
            self.camera_x = min(self.camera_x + self.camera_speed, self.map_width * self.view.tile_size * 2 - screen_width)
        if keys[pygame.K_LEFT]:
            self.camera_x = max(self.camera_x - self.camera_speed, 0)
        if keys[pygame.K_DOWN]:  # Vers le bas
            self.camera_y = min(self.camera_y + self.camera_speed, self.map_height * self.view.tile_size - screen_height)
        if keys[pygame.K_UP]:  # Vers le haut
            self.camera_y = max(self.camera_y - self.camera_speed, 0)
            
        return True  # Continuer la boucle de jeu



    def select_unit(self, mouse_pos):
        """Sélectionne une unité à la position de la souris"""
        for unit in self.model['units']:
            #if unit.x - 10 < mouse_pos[0] < unit.x + 10 and unit.y - 10 < mouse_pos[1] < unit.y + 10:
            if unit.is_clicked(mouse_pos):  
                self.selected_unit = unit
                print(f"Unité {unit.type} sélectionnée à la position {unit.x}, {unit.y}")
                return
        print("Aucune unité sélectionnée")    

    def update(self):
        """Met à jour les unités du modèle et les affiche."""
        # Met à jour les unités
        for unit in self.model['units']:
            unit.update()  # Met à jour l'état de l'unité (déplacement, actions, etc.)
            
        # Rendu des unités avec les coordonnées de la caméra
        self.view.render_units(self.model['units'], self.camera_x, self.camera_y, self.zoom_level)

