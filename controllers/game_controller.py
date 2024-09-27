import pygame
from models.unit import Unit
from models.carte import Carte
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


        # Gérer le clic et le déplacement de la souris
        self.is_dragging = False
        self.last_mouse_pos = None



    def handle_input(self):
        """Gère les événements clavier/souris"""

        # Accéder à la largeur et hauteur de l'écran via la vue
        screen_width = self.view.screen.get_width()
        screen_height = self.view.screen.get_height()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False  # Quitter la boucle de jeu
            
              #Gestion de la souris
                
            # Début du clic gauche (sélection d'une unité ou début du glissement)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Clic gauche
                mouse_pos = pygame.mouse.get_pos()
                # Vérifier si un villageois est sélectionné ou si on commence un déplacement de caméra
                if not self.is_dragging:
                    self.is_dragging = True
                    self.last_mouse_pos = mouse_pos
                else:
                    # Sélectionner l'unité à la position de la souris
                    self.select_unit(mouse_pos)

            # Relâchement du clic gauche (fin du glissement de la caméra)
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
                    
                    # Empêcher la caméra de sortir des limites de la carte
                    self.camera_x = max(0, min(self.camera_x, (120 * 32) - self.view.screen.get_width()))
                    self.camera_y = max(0, min(self.camera_y, (120 * 32) - self.view.screen.get_height()))
                
                # Mettre à jour la dernière position de la souris
                self.last_mouse_pos = current_mouse_pos

            # Défilement de la carte avec la souris si elle touche les bords
            mouse_x, mouse_y = pygame.mouse.get_pos()

             


            # Vérifier si la souris est proche des bords de l'écran
            if mouse_x > screen_width - 20:  # Bord droit
                self.camera_x = min(self.camera_x + self.camera_speed, (120 * 32) - screen_width)
            if mouse_x < 20:  # Bord gauche
                self.camera_x = max(self.camera_x - self.camera_speed, 0)
            if mouse_y > screen_height - 20:  # Bord bas
                self.camera_y = min(self.camera_y + self.camera_speed, (120 * 32) - screen_height)
            if mouse_y < 20:  # Bord haut
                self.camera_y = max(self.camera_y - self.camera_speed, 0)

            # Déplacer une unité avec la touche espace
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:  # Touche espace
                if self.selected_unit:
                    # Déplacer l'unité sélectionnée vers une nouvelle position (clic droit pour déplacer l'unité)
                    new_pos = pygame.mouse.get_pos()
                    self.model.move_unit(self.selected_unit, new_pos)
                
    
        # Gestion des touches de direction pour déplacer la caméra
        keys = pygame.key.get_pressed()
        
        # Déplacement caméra avec touches directionnelles
        if keys[pygame.K_LEFT]:
            self.camera_x = max(self.camera_x - self.camera_speed, 0)
        if keys[pygame.K_RIGHT]:
            self.camera_x = min(self.camera_x + self.camera_speed, self.map_width * self.view.tile_size * 2 - screen_width )
        if keys[pygame.K_UP]:
            self.camera_y = max(self.camera_y - self.camera_speed, 0)
        if keys[pygame.K_DOWN]:
            self.camera_y = min(self.camera_y + self.camera_speed, self.map_height * self.view.tile_size - screen_height)
            
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
        """Met à jour les unités du modèle."""
        for unit in self.model['units']:
            unit.update()  # Met à jour l'état de l'unité (déplacement, actions, etc.)
        # Ne touche pas à l'affichage ici !

