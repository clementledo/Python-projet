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
from models.Resources.Tile import Type
from views.game_view import GameView
from controllers.game_controller import GameController
from models.map import Map
from models.Player.IA import IAPlayer, Strategy
from models.Player.ai import IA
#
import traceback
import json

TILE_SIZE = 10


class GameState:
    """
    Classe pour gérer l'état du jeu.
    """
    STARTING_CONDITIONS = {
        "Maigre": {
            "resources": {"food": 50, "wood": 200, "gold": 50},
            "buildings": [("Town_center", (5, 9))],
            "villagers": 3
        },
        "Moyenne": {
            "resources": {"food": 2000, "wood": 2000, "gold": 2000},
            "buildings": [("Town_center", (5, 9))],
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

    def __init__(self, use_terminal_view=True):
        self.tile_size = 1 if use_terminal_view else 32
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
        self.use_terminal_view = use_terminal_view
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

    def set_screen(self, screen):
        self.screen = screen
        if self.view is None and screen is not None:
            self.view = GameView(screen, self.tile_size)
            self.controller = GameController(
                self.model, 
                self.view, 
                self.carte,  # Pass the map
                self.tile_size  # Pass tile size
            )

    def start_new_game(self, screen, map_width, map_height, tile_size, map_type="ressources_generales", 
                       starting_condition="Marines", use_terminal_view=False, ai_mode=True):
        """Initialize new game with terminal or GUI mode"""
        self.use_terminal_view = use_terminal_view
        
        if use_terminal_view:
            import os
            os.environ['SDL_VIDEODRIVER'] = 'dummy'
        
        # Initialize game components
        self.carte = Map(map_width, map_height, map_type)
        condition = self.STARTING_CONDITIONS[starting_condition]
        self.player_resources = {
            1: condition["resources"].copy(), 
            2: condition["resources"].copy()
        }
        
        # Skip view initialization in terminal mode
        if not use_terminal_view:
            self.set_screen(screen)
        
        units = []
        buildings = []
        
        # Initialize buildings with terminal mode awareness
        for building_type, pos in condition["buildings"]:
            building_class = globals()[building_type]
            building = building_class(pos)
            building.use_terminal_view = use_terminal_view
            building.player_id = 1
            buildings.append(building)

            mirrored_x = map_width - pos[0] - 1
            building = building_class((mirrored_x, pos[1]))
            building.use_terminal_view = use_terminal_view
            building.player_id = 2
            buildings.append(building)

        # Initialize units with terminal mode awareness
        for i in range(condition["villagers"]):
            x_offset = i % 4
            y_offset = i // 4
            
            villager = Villager(10 + x_offset, 12 + y_offset, self.carte)
            villager.use_terminal_view = use_terminal_view
            villager.player_id = 1
            units.append(villager)

            villager = Villager(map_width - 15 + x_offset, 12 + y_offset, self.carte)
            villager.use_terminal_view = use_terminal_view
            villager.player_id = 2
            units.append(villager)
        
        for building in buildings:
            self.carte.place_building(building)
        self.model = {'map': self.carte, 'units': units, 'buildings': buildings}
        
        # Initialize AI players
        if ai_mode:
            self.players = {
                1: IAPlayer(1, self, Strategy.AGGRESSIVE),
                #2: IAPlayer(2, self, Strategy.DEFENSIVE)
                2: IA(2, self, Strategy.ECONOMIC) 
            }

        # Initialize view and controller
        if not use_terminal_view:
            self.view = GameView(screen, tile_size)
            self.view.game_state = self  # Pass game_state reference to view
            self.carte.resources = self.player_resources  # Pass both players' resources
            
            self.view.load_unit_sprite('Villager', 'assets/villager.png')
            self.view.load_unit_sprite('Archer', 'assets/archer.png')
            self.view.load_unit_sprite('Horseman', 'assets/horseman.png')

            self.view.load_building_sprite("T", "assets/Buildings/Towncenter.png")
            self.view.load_building_sprite("A", "assets/Buildings/Archery_range.png")
            self.view.load_building_sprite("B", "assets/Buildings/Barracks.png")
            self.view.load_building_sprite("H", "assets/Buildings/House.png")
            self.view.load_building_sprite("F", "assets/Buildings/Farm.jpg")
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
                "resources_on_map": [(pos, amount) for pos, amount in self.model['map'].resources.items()]
            }
            
            # Generate new save filename
            if filepath is None:
                save_num = self.get_next_save_number()
                filepath = os.path.join(self.save_dir, f"save_game{save_num}.pkl")

            try:
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                with open(filepath, 'wb') as save_file:
                    pickle.dump(save_data, save_file, protocol=pickle.HIGHEST_PROTOCOL)
                print(f"Game saved as {filepath}!")
                return True
            except Exception as e:
                print(f"Save error: {e}")
                return False
            
################# Load game state from file #################
    def load_map_and_camera(self, data):
        """Load map and camera settings."""
        self.model['map'] = Map.deserialize(data["map"])
        self.carte = self.model['map']
        self.camera_x = data["camera_x"]
        self.camera_y = data["camera_y"]
        self.zoom_level = data["zoom_level"]
        print("Map and camera successfully loaded.")

    def load_buildings(self, data):
        """Load buildings from saved data."""
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

    def load_units(self, data):
        """Load units from saved data."""
        self.model['units'] = []
        for unit_data in data["units"]:
            if unit_data["unit_type"] == "Villager":
                unit = Villager.deserialize(unit_data, self.model['map'])
                self.model['units'].append(unit)
        print(f"{len(self.model['units'])} units successfully loaded.")

    def load_sprites(self):
        """Load all required sprites."""
        self.view.load_building_sprite('T', "assets/Buildings/Towncenter.png")
        self.view.load_unit_sprite('Villager', "assets/Sprites/Villager/Stand/Villagerstand001.png")
        print("Sprites loaded successfully.")

    def initialize_controller(self):
        """Initialize the game controller."""
        self.controller = GameController(self.model, self.view, self.carte, self.tile_size)
        self.controller.camera_x = self.camera_x
        self.controller.camera_y = self.camera_y
        self.controller.zoom_level = self.zoom_level

    def initialize_game_components(self, screen, TILE_SIZE):
        """Initialize game components after loading."""
        self.screen = screen
        self.view = GameView(screen, TILE_SIZE)
        
        # Load all required sprites
        self.load_sprites()
        
        # Initialize game controller with all components
        self.initialize_controller()
        
        # Ensure resource panel is visible
        self.view.show_resource_panel = True

    def load_state(self, filepath):
        """Load game state from a file."""
        try:
            
            
            # Check if file exists
            if not os.path.exists(filepath):
                print(f"Save file not found: {filepath}")
                return False
                
            # Load binary data using pickle
            with open(filepath, 'rb') as file:
                data = pickle.load(file)
            
            self.load_map_and_camera(data)
            self.load_buildings(data)
            self.load_units(data)
            
            print(f"Game state loaded successfully from {filepath}")
            return True
            
        except FileNotFoundError:
            print(f"Save file not found: {filepath}")
            return False
        except pickle.UnpicklingError as e:
            print(f"Error unpickling save file: {e}")
            return False
        except Exception as e:
            print(f"Error loading game state: {e}")
            return False

    

################# END Load game state from file #################

    def show_fps(self, clock, font, screen):
        """Display FPS on the screen."""
        clock.tick()
        fps = clock.get_fps()
        fps_text = font.render(f"FPS: {int(fps)}", True, (255, 255, 255))
        screen.blit(fps_text, (10, 10))

    def update_ai(self):
        """Update AI players each frame."""
        if hasattr(self, 'players'):
            for player in self.players.values():
                player.update()

    def update_and_render(self):
        """Update game state and render."""
        if self.view and self.controller:
            self.screen.fill((0, 0, 0))
            self.view.render(self.model, self.camera_x, self.camera_y, self.zoom_level)
           # pygame.display.flip()

    def remove_unit(self, unit):
        """Remove a unit from game state and cleanup all references"""
        # Remove from units list
        if unit in self.model['units']:
            self.model['units'].remove(unit)
        
        # Remove from map occupancy
        if hasattr(unit, 'x') and hasattr(unit, 'y'):
            self.carte.grid[unit.y][unit.x].occupant = None
            
        # Remove unit status
        if unit in self.unit_status:
            del self.unit_status[unit]
            
        # Update any relevant player statistics
        if hasattr(unit, 'player_id'):
            player_id = unit.player_id
            if player_id in self.players:
                self.players[player_id].unit_count = len([u for u in self.model['units'] if u.player_id == player_id])