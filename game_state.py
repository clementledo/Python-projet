import pickle
from models.units.villager import Villager
from models.units.archer import Archer
from models.units.horseman import Horseman
from models.Buildings.town_center import Town_center
from models.Buildings.archery_range import Archery_Range
from models.Buildings.building import Building
from models.units.unit import Unit
from models.Resources.Tile import Type
from views.game_view import GameView
from controllers.game_controller import GameController
from models.map import Map
import pygame

TILE_SIZE = 50


class GameState:
    """
    Classe pour gérer l'état du jeu.
    """
    def __init__(self):
        self.current_state = "main_menu"  # État initial du jeu
        self.running = True  # Flag pour savoir si le jeu tourne
        self.model = None  # Le modèle du jeu (sera initialisé plus tard)
        self.view=None
        self.camera_x = 0  
        self.camera_y = 0
        self.zoom_level=1.0

    def start_new_game(self, screen, screen_width, screen_height, tile_size,use_terminal_view=False):
        # Calculate map size based on screen dimensions
        tiles_x = int(screen_width / (tile_size * 2)) + 20
        tiles_y = int(screen_height / tile_size) + 20

        # Create map
        self.carte = Map(tiles_x, tiles_y)
        self.carte.generer_aleatoire(type_carte="ressources_generales") 
        self.carte.get_tile(10,15).occupant = Type.Town_center
        self.carte.get_tile(10,14).occupant = Type.Town_center
        self.carte.get_tile(11,15).occupant = Type.Town_center
        self.carte.get_tile(11,14).occupant = Type.Town_center
        # Initialize units
        units = [
            Villager(18, 12, self.carte),
            Villager(3, 26, self.carte),
            Archer(20, 12, self.carte),
            Horseman(20, 15, self.carte)
        ]
        #Initialize buildings
        buildings =[
            Town_center((10, 10)),
            Archery_Range((10,26)),
            Archery_Range((14,10))
        ]
        self.model = {'map':self.carte,'units': units,'buildings':buildings}

        # Initialize view and controller
        

        if not use_terminal_view:
            from views.game_view import GameView  # Import uniquement si nécessaire
            self.view = GameView(screen, tile_size)
            
            self.view.load_unit_sprite('Villager', 'assets/villager.png')
            self.view.load_unit_sprite('Archer', 'assets/archer.png')
            self.view.load_unit_sprite('Horseman', 'assets/horseman.png')

            self.view.load_building_sprite("T", "assets/Buildings/Towncenter.png")
            self.view.load_building_sprite("A", "assets/Buildings/Archery_range.png")
            self.view.generate_resources(self.carte)

            self.controller = GameController(self.model, self.view, self.carte,tile_size)
        else:
                self.view = None
    
    def change_state(self, new_state):
        """Change l'état actuel du jeu."""
        self.current_state = new_state

    def is_running(self):
        """Vérifie si le jeu doit continuer."""
        return self.running

    def stop(self):
        """Arrête la boucle principale du jeu."""
        self.running = False

    def save_state(self, filepath="save_game.pkl"):
        """Sauvegarde l'état actuel du jeu."""
        if self.model:
            save_data = {
                "map": self.model['map'].serialize(),  # Serialize the map
                "units": [unit.serialize() for unit in self.model['units']],
                "buildings": [building.serialize() for building in self.model['buildings']],
                "camera_x": self.camera_x,
                "camera_y": self.camera_y,
                "zoom_level": self.zoom_level,
            }
            try:
                with open(filepath, "wb") as save_file:
                    pickle.dump(save_data, save_file)
                print("Game saved!")
            except Exception as e:
                print(f"Erreur lors de la sauvegarde : {e}")
        else:
            print("Aucun modèle de jeu à sauvegarder.")


    def load_state(self, filepath="save_game.pkl"):
        try:
            with open(filepath, "rb") as save_file:
                data = pickle.load(save_file)

            print("Données chargées depuis le fichier :", data)
            print("Carte avant désérialisation :", data["map"])
            print("Unités avant désérialisation :", data["units"])
            print("Bâtiments avant désérialisation :", data["buildings"])

            # Désérialisation des objets
            print("Chargement de la carte...")
            carte = Map.deserialize(data["map"])
            print("Carte désérialisée :", carte)
            print("Carte chargée.")

            print("Chargement des unités...")
            units = [Unit.deserialize(unit_data, carte) for unit_data in data["units"]]
            print("Unités chargées.")

            print("Chargement des bâtiments...")
            buildings = [Building.deserialize(building_data) for building_data in data["buildings"]]
            print("Bâtiments chargés.")

            print("Unités désérialisées :", units)
            print("Bâtiments désérialisés :", buildings)

            # Mise à jour de l'état du jeu
            self.model = {"units": units, "buildings": buildings}
            self.carte = carte
            self.camera_x = data["camera_x"]
            self.camera_y = data["camera_y"]
            self.zoom_level = data["zoom_level"]

            # Réinitialisation de la vue
            info_object = pygame.display.Info()  # Obtenir les dimensions de l'écran
            screen_width, screen_height = info_object.current_w, info_object.current_h
            screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
            self.view = GameView(screen, tile_size=TILE_SIZE)

            if not self.view:
                print("Erreur : Vue non initialisée.")
            else:
                print("Vue initialisée avec succès.")

            # Charger les sprites des unités et bâtiments
            try:
                self.view.load_unit_sprite('Villager', 'assets/villager.png')
            except Exception as e:
                print("Erreur lors du chargement du sprite de Villager :", e)
           
            self.view.load_unit_sprite('Archer', 'assets/archer.png')
            self.view.load_unit_sprite('Horseman', 'assets/horseman.png')

            self.view.load_building_sprite("T", "assets/Buildings/Towncenter.png")
            self.view.load_building_sprite("A", "assets/Buildings/Archery_range.png")
            self.view.generate_resources(self.carte)

            # Réinitialisation du contrôleur
            self.controller = GameController(self.model, self.view, self.carte, TILE_SIZE)

            # Mise à jour visuelle immédiate
            self.view.render_map(self.carte, self.camera_x, self.camera_y, self.zoom_level)
            self.view.render_units(units, self.camera_x, self.camera_y, self.zoom_level, self.controller.selected_unit)
            self.view.render_buildings(buildings, self.camera_x, self.camera_y, self.zoom_level)
            self.view.render_minimap(self.carte, self.camera_x, self.camera_y, self.zoom_level, units, buildings)

            print("État du jeu chargé avec succès.")

        except Exception as e:
            print(f"Erreur lors du chargement de l'état du jeu : {e}")


    def show_fps(slef,clock,font,screen):
        
        clock.tick()
         # Calcul des FPS
        fps = clock.get_fps()
        
        # Afficher les FPS sur l'écran
        fps_text = font.render(f"FPS: {int(fps)}", True, (255, 255, 255))
        screen.blit(fps_text, (10, 10))

