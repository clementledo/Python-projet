import pickle
import os
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
import traceback

TILE_SIZE = 50


class GameState:
    """
    Classe pour gérer l'état du jeu.
    """
    STARTING_CONDITIONS = {
        "Maigre": {
            "resources": {"food": 50, "wood": 200, "gold": 50},
            "buildings": [("Town_center", (10, 9))],
            "villagers": 3
        },
        "Moyenne": {
            "resources": {"food": 2000, "wood": 2000, "gold": 2000},
            "buildings": [("Town_center", (10, 9))],
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

    def __init__(self, screen=None):
        self.screen = screen
        self.tile_size = 32
        self.model = {'map': None, 'units': [], 'buildings': []}
        self.view = None
        self.controller = None
        self.running = True
        self.players = {}
        self.carte = None
        self.camera_x = 0
        self.camera_y = 0
        self.zoom_level = 1
        self.player_resources = {}
        self.save_dir = "save_games"
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

    def set_screen(self, screen):
        self.screen = screen
        if self.view is None and screen is not None:
            self.view = GameView(screen, self.tile_size)
            self.controller = GameController(self.model, self.view)

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

    def get_next_save_number(self):
        """Get next available save number"""
        files = [f for f in os.listdir(self.save_dir) if f.startswith("save_game")]
        if not files:
            return 0
        numbers = [int(f.replace("save_game", "").replace(".pkl", "")) for f in files if f.replace("save_game", "").replace(".pkl", "").isdigit()]
        return max(numbers + [0]) + 1

    def get_latest_save(self):
        """Get most recent save file"""
        files = [f for f in os.listdir(self.save_dir) if f.startswith("save_game")]
        if not files:
            return None
        numbers = [int(f.replace("save_game", "").replace(".pkl", "")) for f in files if f.replace("save_game", "").replace(".pkl", "").isdigit()]
        if not numbers:
            return os.path.join(self.save_dir, "save_game.pkl")
        latest = max(numbers)
        return os.path.join(self.save_dir, f"save_game{latest}.pkl")

    def save_state(self, filepath=None):
        if self.model:
            save_data = {
                "map": self.model['map'].serialize(),
                "units": [unit.serialize() for unit in self.model['units']],
                "buildings": [building.serialize() for building in self.model['buildings']],
                "camera_x": self.camera_x,
                "camera_y": self.camera_y,
                "zoom_level": self.zoom_level,
                "player_resources": self.player_resources,
                "resources_on_map": [(resource.position, resource.serialize()) 
                                   for resource in self.model['map'].resources]
            }
            
            # Generate new save filename
            if filepath is None:
                save_num = self.get_next_save_number()
                filepath = os.path.join(self.save_dir, f"save_game{save_num}.pkl")

            try:
                with open(filepath, "wb") as save_file:
                    pickle.dump(save_data, save_file)
                print(f"Game saved as {filepath}!")
                return True
            except Exception as e:
                print(f"Save error: {e}")
                return False

    def load_state(self, filename=None):
        if filename is None:
            filename = self.get_latest_save()
            if filename is None:
                print("No save files found!")
                return False
        
        try:
            print(f"Loading save file: {filename}")

            # Charger les données à partir du fichier
            with open(filename, 'rb') as f:
                data = pickle.load(f)
            
            print("Data successfully loaded from file.")

            # Vérification des données essentielles
            required_keys = ["map", "camera_x", "camera_y", "zoom_level", "buildings", "units"]
            for key in required_keys:
                if key not in data:
                    raise KeyError(f"Missing required key in saved data: {key}")
            
            # Charger la carte
            self.model['map'] = Map.deserialize(data["map"])
            self.carte = self.model['map']
            self.camera_x = data["camera_x"]
            self.camera_y = data["camera_y"]
            self.zoom_level = data["zoom_level"]
            print("Map and camera successfully loaded.")

            # Charger les bâtiments
            self.model['buildings'] = []
            for building_data in data["buildings"]:
                if building_data["name"] == "Town_center":
                    x, y = building_data["pos"]
                    building = Town_center(pos=(x, y))
                    building.size = building_data["size"]
                    building.hp = building_data["hp"]
                    building.useable = building_data["useable"]
                    self.model['buildings'].append(building)
            print(f"{len(self.model['buildings'])} buildings successfully loaded.")

            # Charger les unités
            self.model['units'] = []
            for unit_data in data["units"]:
                if unit_data["unit_type"] == "Villager":
                    unit = Villager.deserialize(unit_data, self.model['map'])
                    self.model['units'].append(unit)
            print(f"{len(self.model['units'])} units successfully loaded.")

            # Initialiser les composants de jeu
            if self.screen:
                print("Initializing game components...")
                
                # Effacer l'écran
                self.screen.fill((0, 0, 0))
                pygame.display.flip()

                # Charger les sprites et la vue
                self.view = GameView(self.screen, self.tile_size)
                self.view.load_building_sprite('T', "assets/Buildings/Towncenter.png")
                self.view.load_unit_sprite('Villager', "assets/Sprites/Villager/Stand/Villagerstand001.png")
                print("Sprites loaded successfully.")

                # Initialiser le contrôleur
                self.controller = GameController(self.model, self.view, self.carte, self.tile_size)
                self.controller.camera_x = self.camera_x
                self.controller.camera_y = self.camera_y
                self.controller.zoom_level = self.zoom_level
                print("Controller initialized successfully.")

                # Pause pour s'assurer que l'affichage est mis à jour
                pygame.time.wait(100)
                print("Game loaded successfully!")
                return True

        except KeyError as e:
            print(f"KeyError: {e}")
            traceback.print_exc()
        except FileNotFoundError:
            print(f"File not found: {filename}")
        except Exception as e:
            print(f"Error loading game state: {e}")
            traceback.print_exc()
        
        print("Load sequence failed.")
        return False

    def load_state1(self, filename):
        try:
            print("Starting load sequence...")
            with open(filename, 'rb') as f:
                data = pickle.load(f)
            
            # Reset game state
            self.model = {
                'map': None,
                'units': [],
                'buildings': []
            }
            
            # Load map and state
            self.model['map'] = Map.deserialize(data["map"])
            self.carte = self.model['map']
            self.camera_x = data["camera_x"]
            self.camera_y = data["camera_y"]
            self.zoom_level = data["zoom_level"]
            
            # Load buildings
            for building_data in data["buildings"]:
                if building_data["name"] == "Town_center":
                    x, y = building_data["pos"]
                    building = Town_center(pos=(x, y))
                    building.size = building_data["size"]
                    building.hp = building_data["hp"]
                    building.useable = building_data["useable"]
                    building.player_id = building_data.get("player_id", 1)
                    self.model['buildings'].append(building)

            # Load units
            for unit_data in data["units"]:
                if unit_data["unit_type"] == "Villager":
                    unit = Villager.deserialize(unit_data, self.model['map'])
                    self.model['units'].append(unit)

            # Initialize game components
            if self.screen:
                self.view = GameView(self.screen, self.tile_size)
                self.controller = GameController(self.model, self.view, self.carte, self.tile_size)
                self.controller.camera_x = self.camera_x
                self.controller.camera_y = self.camera_y
                self.controller.zoom_level = self.zoom_level
                
                # Ensure resources are loaded
                if hasattr(data, 'player_resources'):
                    self.player_resources = data['player_resources']
                
                self.running = True
                return True
                
        except Exception as e:
            print(f"Error loading game state: {e}")
            traceback.print_exc()
            return False

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

    def update_and_render(self):
        """Update game state and render"""
        if self.view and self.controller:
            self.screen.fill((0, 0, 0))
            self.view.render(self.model, self.camera_x, self.camera_y, self.zoom_level)
            pygame.display.flip()

