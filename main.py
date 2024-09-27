import pygame

from models.unit import Unit
from views.game_view import GameView
from controllers.game_controller import GameController
from models.carte import Carte
from views.terminalView import TerminalView

# Initialisation de Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600),pygame.DOUBLEBUF)
pygame.display.set_caption('Age of Empires en Pygame - MVC')

# Créer un objet pour limiter le framerate
clock = pygame.time.Clock()

# Créer le modèle (ensemble d'unités)
units = [Unit(100, 100, 'guerrier'), Unit(200, 150, 'archer')]
model = {'units': units}

# Demander à l'utilisateur de choisir un type de carte (par exemple avec un input simple)
type_carte = "ressources_generales" #input("Choisir le type de carte : ressources_generales ou or_central ? ")

# Initialisation de la carte et de la vue
carte = Carte(120, 120)  # Créer une carte de 120x120 tuiles
carte.generer_aleatoire(type_carte)  # Générer une carte aléatoire

# Créer la vue et charger les sprites
view = GameView(screen)
view.load_unit_sprite('guerrier', 'assets/Axethrower.png')
view.load_unit_sprite('archer', 'assets/archer.png')


 #Créer le contrôleur
controller = GameController(model, view)

# Boucle de jeu
running = True
while running:

    running = controller.handle_input()  # Gestion des entrées utilisateur
    



    controller.update()  # Met à jour l'affichage des units

    #Effacer l'écran
    screen.fill((0, 0, 0))
    
    mode = input("Mode d'affichage (graphique/terminal) : ").strip().lower()
    if mode == 'graphique':
        view.render_background()  # Effacer l'écran
        
        #Afficher la carte (géré par la vue)
        view.render_map(carte,controller.camera_x, controller.camera_y)  # Afficher la carte
        
        view.update_display()  # Mettre à jour l'affichage
        
        # Rafraîchir l'écran
        pygame.display.flip()  # ou pygame.display.update()
    elif mode == 'terminal':
        TerminalView.display_map(units)

     # Limite le framerate à 60 images par seconde
    clock.tick(60)


# Quitter Pygame
pygame.quit()
