import pickle
from models.units.villager import Villager
from models.units.archer import Archer
from models.units.horseman import Horseman
from models.Buildings.town_center import Town_center
from models.Buildings.archery_range import Archery_Range
from views.game_view import GameView
from controllers.game_controller import GameController
from models.map import Map


class GameState:
    """
    Classe pour gérer l'état du jeu.
    """
    def __init__(self):
        self.current_state = "main_menu"  # État initial du jeu
        self.running = True  # Flag pour savoir si le jeu tourne
        self.model = None  # Le modèle du jeu (sera initialisé plus tard)

    def start_new_game(self, screen, screen_width, screen_height, tile_size):
        # Calculate map size based on screen dimensions
        tiles_x = int(screen_width / (tile_size * 2)) + 20
        tiles_y = int(screen_height / tile_size) + 20

        # Create map
        self.carte = Map(tiles_x, tiles_y)
        self.carte.generer_aleatoire(type_carte="ressources_generales")

        # Initialize units
        units = [
            Villager(15, 12, self.carte),
            Villager(3, 26, self.carte),
            Archer(20, 12, self.carte),
            Horseman(20, 15, self.carte)
        ]
        #Initialize buildings
        buildings =[
            Town_center((10, 10)),
            Archery_Range((10,26))
        ]
        self.model = {'units': units,'buildings':buildings}

        # Initialize view and controller
        self.view = GameView(screen, tile_size=tile_size)
        self.view.load_unit_sprite('Villager', 'assets/villager.png')
        self.view.load_unit_sprite('Archer', 'assets/archer.png')
        self.view.load_unit_sprite('Horseman', 'assets/horseman.png')

        self.view.load_building_sprite("T", "assets/Buildings/Towncenter.png")
        self.view.load_building_sprite("A", "assets/Buildings/Archery_range.png")
        self.view.generate_decorations(self.carte)

        self.controller = GameController(self.model, self.view, self.carte,tile_size)

    
    def change_state(self, new_state):
        """Change l'état actuel du jeu."""
        self.current_state = new_state

    def is_running(self):
        """Vérifie si le jeu doit continuer."""
        return self.running

    def stop(self):
        """Arrête la boucle principale du jeu."""
        self.running = False

    def save_state(self, filepath="savegame.pkl"):
        """Sauvegarde l'état actuel du jeu."""
        if self.model:
            with open(filepath, "wb") as save_file:
                
                pickle.dump(self.model, save_file)
        else:
            print("Aucun modèle de jeu à sauvegarder.")

    def load_state(self, filepath="save_game.pkl"):
        """Charge un état de jeu depuis une sauvegarde."""
        try:
            with open(filepath, "rb") as save_file:
                
                self.model = pickle.load(save_file)
        except FileNotFoundError:
            print("Aucune sauvegarde trouvée.")
