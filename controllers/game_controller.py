import pygame
from models.unit import Unit

class GameController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.selected_unit = None  # Unité sélectionnée par le joueur
        self.camera_x = 0 # Position X de la caméra
        self.camera_y = 0 # Position y de la caméra
        self.camera_speed = 10 # Vitesse de déplacement de la caméra
        self.select_unit = None



    def handle_input(self):
        """Gère les événements clavier/souris"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False  # Quitter la boucle de jeu
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Clic gauche
                mouse_pos = pygame.mouse.get_pos()
                self.select_unit(mouse_pos)
                
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:  # Touche espace
                if self.selected_unit:
                    # Déplacer l'unité sélectionnée vers une nouvelle position
                    new_pos = pygame.mouse.get_pos()
                    self.model.move_unit(self.selected_unit, new_pos)
    
        # Gestion des touches de direction pour déplacer la caméra
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT]:
            self.camera_x = max(self.camera_x - self.camera_speed, 0)
        if keys[pygame.K_RIGHT]:
            self.camera_x = min(self.camera_x + self.camera_speed, (120 * 32) - self.view.screen.get_width())
        if keys[pygame.K_UP]:
            self.camera_y = max(self.camera_y - self.camera_speed, 0)
        if keys[pygame.K_DOWN]:
            self.camera_y = min(self.camera_y + self.camera_speed, (120 * 32) - self.view.screen.get_height())
            
        return True  # Continuer la boucle de jeu

    def select_unit(self, mouse_pos):
        """Sélectionne une unité à la position de la souris"""
        for unit in self.model['units']:
            #if unit.x - 10 < mouse_pos[0] < unit.x + 10 and unit.y - 10 < mouse_pos[1] < unit.y + 10:
            if unit.is_clicked(mouse_pos):  
                self.selected_unit = unit
                print(f"Unité {unit.type} sélectionnée à la position {unit.x}, {unit.y}")
                break

    def update(self):
        """Met à jour les unités du modèle."""
        for unit in self.model['units']:
            unit.update()  # Met à jour l'état de l'unité (déplacement, actions, etc.)
        # Ne touche pas à l'affichage ici !

