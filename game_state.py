import pickle
from models.units.villager import Villager
from models.units.archer import Archer
from models.units.horseman import Horseman
from models.Buildings.town_center import Town_center
from models.Buildings.archery_range import Archery_Range
from models.Buildings.building import Building
from models.Buildings.barrack import Barrack
from models.units.unit import Unit
from views.game_view import GameView
from controllers.game_controller import GameController
from models.map import Map
from models.Player.IA import IAPlayer, Strategy
import pygame

TILE_SIZE = 50


class GameState:
    """
    Classe pour gérer l'état du jeu.
    """
    STARTING_CONDITIONS = {
        "Maigre": {
            "resources": {"food": 50, "wood": 200, "gold": 50},
            "buildings": [("Town_center", (10, 10))],
            "villagers": 3
        },
        "Moyenne": {
            "resources": {"food": 2000, "wood": 2000, "gold": 2000},
            "buildings": [("Town_center", (10, 10))],
            "villagers": 3
        },
        "Marines": {
            "resources": {"food": 20000, "wood": 20000, "gold": 20000},
            "buildings": [
                # Base principale
                ("Town_center", (15, 15)),    # Centre ville principal
                ("Barrack", (20, 15)),        # Caserne proche du centre
                ("Archery_Range", (15, 20)),  # Camp de tir proche du centre
                
                # Base secondaire gauche
                ("Town_center", (10, 40)),    # Second centre ville
                ("Barrack", (15, 40)),        # Caserne de support
                
                # Base secondaire droite
                ("Town_center", (40, 10)),    # Troisième centre ville
                ("Archery_Range", (40, 15))   # Camp de tir de support
            ],
            "villagers": 15
        }
    }

    def __init__(self):
        self.running = True
        self.players = {}
        self.model = {}
        self.view = None
        self.controller = None
        self.carte = None
        self.camera_x = 0
        self.camera_y = 0
        self.zoom_level = 1
        self.player_resources = {}

    def start_new_game(self, screen, map_width, map_height, tile_size, map_type="ressources_generales", starting_condition="Marines", use_terminal_view=False, ai_mode=True):
        # Initialize map, units, buildings, and resources
        self.carte = Map(map_width, map_height, map_type)  # Corrected constructor call
        condition = self.STARTING_CONDITIONS[starting_condition]
        self.player_resources = {1: condition["resources"].copy(), 2: condition["resources"].copy()}
        
        units = []
        buildings = []

        # Initialize buildings
        for building_type, pos in condition["buildings"]:
            building_class = globals()[building_type]
            building = building_class(pos)
            building.player_id = 1
            buildings.append(building)

            mirrored_x = map_width - pos[0] - 1
            building = building_class((mirrored_x, pos[1]))
            building.player_id = 2
            buildings.append(building)

        # Initialize units
        for i in range(condition["villagers"]):
            x_offset = i % 4
            y_offset = i // 4
            villager = Villager(10 + x_offset, 12 + y_offset, self.carte)
            villager.player_id = 1
            units.append(villager)
            
            villager = Villager(map_width - 15 + x_offset, 12 + y_offset, self.carte)
            villager.player_id = 2
            units.append(villager)

        self.model = {'map': self.carte, 'units': units, 'buildings': buildings}
        
        # Initialize AI players
        if ai_mode:
            self.players = {
                1: IAPlayer(1, self, Strategy.AGGRESSIVE),
                2: IAPlayer(2, self, Strategy.DEFENSIVE)
            }

        # Initialize view and controller
        if not use_terminal_view:
            self.view = GameView(screen, tile_size)
            self.view.game_state = self  # Pass game_state reference to view
            self.carte.resources = self.player_resources  # Pass both players' resources
            
            self.view.load_unit_sprite('Villager', 'assets/villager.png')
            self.view.load_unit_sprite('Archer', 'assets/archer.png')
            #self.view.load_unit_sprite('Horseman', 'assets/horseman.png')

            self.view.load_building_sprite("T", "assets/Buildings/Towncenter.png")
            self.view.load_building_sprite("A", "assets/Buildings/Archery_range.png")
            self.view.load_building_sprite("B", "assets/Buildings/Barracks.png")

            self.controller = GameController(self.model,self.view, self.carte, tile_size)  # Pass required arguments

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

    def update_ai(self):
        """Update AI players each frame"""
        if hasattr(self, 'players'):
            for player in self.players.values():
                player.update()

    def run_game_loop(self):
        """Main game loop with AI updates"""
        clock = pygame.time.Clock()
        font = pygame.font.Font(None, 36)

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self.controller.handle_input()

            # Update AI players
            self.update_ai()

            # Update display
            if self.view:
                self.view.render_map(self.carte, self.camera_x, self.camera_y, self.zoom_level)
                self.view.render_units(self.model['units'], self.camera_x, self.camera_y, self.zoom_level, self.controller.selected_unit)
                self.view.render_buildings(self.model['buildings'], self.camera_x, self.camera_y, self.zoom_level)
                self.view.generate_resources(self.carte)
                self.view.render_minimap(self.carte, self.camera_x, self.camera_y, self.zoom_level, self.model['units'], self.model['buildings'])
                
                self.show_fps(clock, font, self.view.screen)
                pygame.display.flip()
                
            clock.tick(60)

