import curses
from enum import Enum
from controllers.game_controller import GameController
from models.Buildings.town_center import Town_center  # Adjust the import path as necessary
import subprocess
import sys


class GameScreen(Enum):
    MAIN_MENU = "main_menu"
    SETTINGS = "settings"
    GAMEPLAY = "gameplay"
    PAUSE = "pause"

MAP_SIZES = {
    "Small": (30, 30),
    "Medium": (75, 75),
    "Large": (120, 120)
}

STARTING_CONDITIONS = ["Maigre", "Moyenne", "Marines"]
TILE_SIZE = 4  # Define TILE_SIZE with an appropriate value
MAP_TYPES = ["ressources_generales","centre_ressources"]

class TerminalView:
    def __init__(self, game_state):
        self.game_state = game_state
        self.camera_x = 0
        self.camera_y = 0
        self.screen = GameScreen.MAIN_MENU
        self.running = True
        self.selected_option = 0
        self.selected_map_size = "Medium"
        self.selected_starting_condition = "Moyenne"
        self.selected_map_type = "ressources_generales"
        self.game_controller = None

    def main_menu(self, stdscr):
        """Affiche et gère le menu principal."""
        stdscr.clear()
        menu_options = ["Nouvelle Partie", "Charger une Partie", "Paramètres", "Quitter"]
        
        while self.screen == GameScreen.MAIN_MENU:
            stdscr.clear()
            stdscr.addstr(0, 0, "=== MENU PRINCIPAL ===")
            for idx, option in enumerate(menu_options):
                if idx == self.selected_option:
                    stdscr.addstr(idx + 2, 2, f"> {option} <", curses.A_REVERSE)
                else:
                    stdscr.addstr(idx + 2, 2, option)

            key = stdscr.getch()

            if key == curses.KEY_UP:
                self.selected_option = (self.selected_option - 1) % len(menu_options)
            elif key == curses.KEY_DOWN:
                self.selected_option = (self.selected_option + 1) % len(menu_options)
            elif key == curses.KEY_ENTER or key in [10, 13]:
                if self.selected_option == 0:  # Nouvelle Partie
                    self.start_new_game(stdscr)
                elif self.selected_option == 1:  # Charger une Partie
                    self.load_game(stdscr)
                elif self.selected_option == 2:  # Paramètres
                    self.screen = GameScreen.SETTINGS
                    self.settings_menu(stdscr)
                elif self.selected_option == 3: 
                     # Quitter
                    self.running = False
                    return

    def pause_menu(self, stdscr):
        """Affiche et gère le menu de pause."""
        pause_options = ["Reprendre", "Sauvegarder", "Charger une Partie", "Menu Principal", "Quitter"]
        selected_pause_option = 0
        
        while self.screen == GameScreen.PAUSE:
            stdscr.clear()
            stdscr.addstr(0, 0, "=== MENU PAUSE ===")
            for idx, option in enumerate(pause_options):
                if idx == selected_pause_option:
                    stdscr.addstr(idx + 2, 2, f"> {option} <", curses.A_REVERSE)
                else:
                    stdscr.addstr(idx + 2, 2, option)

            key = stdscr.getch()

            if key == curses.KEY_UP:
                selected_pause_option = (selected_pause_option - 1) % len(pause_options)
            elif key == curses.KEY_DOWN:
                selected_pause_option = (selected_pause_option + 1) % len(pause_options)
            elif key == curses.KEY_ENTER or key in [10, 13]:
                if selected_pause_option == 0:  # Reprendre
                    self.screen = GameScreen.GAMEPLAY
                elif selected_pause_option == 1:  # Sauvegarder
                    self.game_state.save_state()
                    stdscr.addstr(len(pause_options) + 3, 2, "Jeu sauvegardé.")
                    stdscr.refresh()
                    stdscr.getch()
                elif selected_pause_option == 2:  # Charger une Partie
                    self.load_game(stdscr)
                elif selected_pause_option == 3:  # Menu Principal
                    self.screen = GameScreen.MAIN_MENU
                elif selected_pause_option == 4:  # Quitter
                    self.running = False
                    return

    def start_new_game(self, stdscr):
        """Démarre une nouvelle partie avec les paramètres sélectionnés."""
        map_width, map_height = MAP_SIZES[self.selected_map_size]
        starting_condition = self.selected_starting_condition
        map_type = self.selected_map_type
        self.game_state.start_new_game(stdscr, map_width, map_height, TILE_SIZE, map_type, starting_condition, use_terminal_view=True)
        
        
        self.move_unit_to_town_center() 
        self.screen = GameScreen.GAMEPLAY
        self.gameplay_loop(stdscr)
    
    def move_unit_to_town_center(self):
        # Find town center
        town_center = None
        for building in self.game_state.model['buildings']:
            if isinstance(building, Town_center):
                town_center = building
                break
        
        if town_center:
                self.game_state.model['units'][3].move_towards(town_center.pos, self.game_state.carte)

    def load_game(self, stdscr):
        """Charge une partie sauvegardée."""
        save_path = self.game_state.get_latest_save()
        if save_path and self.game_state.load_state(save_path):
            self.screen = GameScreen.GAMEPLAY
            self.gameplay_loop(stdscr)
        else:
            stdscr.addstr(10, 0, "Aucune sauvegarde trouvée.")
            stdscr.getch()

    def settings_menu(self, stdscr):
        """Affiche et gère le menu des paramètres."""
        stdscr.clear()
        settings_options = ["Taille de la carte", "Condition de départ", "Type de carte", "Retour"]
        selected_setting = 0
        
        while self.screen == GameScreen.SETTINGS:
            stdscr.clear()
            stdscr.addstr(0, 0, "=== PARAMÈTRES ===")
            for idx, option in enumerate(settings_options):
                if idx == selected_setting:
                    stdscr.addstr(idx + 2, 2, f"> {option} <", curses.A_REVERSE)
                else:
                    stdscr.addstr(idx + 2, 2, option)

            if selected_setting == 0:
                stdscr.addstr(6, 2, f"Taille de la carte: {self.selected_map_size}")
            elif selected_setting == 1:
                stdscr.addstr(6, 2, f"Condition de départ: {self.selected_starting_condition}")
            elif selected_setting == 2:
                stdscr.addstr(6, 2, f"Type de carte: {self.selected_map_type}")

            key = stdscr.getch()

            if key == curses.KEY_UP:
                selected_setting = (selected_setting - 1) % len(settings_options)
            elif key == curses.KEY_DOWN:
                selected_setting = (selected_setting + 1) % len(settings_options)
            elif key == curses.KEY_ENTER or key in [10, 13]:
                if selected_setting == 0:  # Taille de la carte
                    self.selected_map_size = self.cycle_option(MAP_SIZES.keys(), self.selected_map_size)
                elif selected_setting == 1:  # Condition de départ
                    self.selected_starting_condition = self.cycle_option(STARTING_CONDITIONS, self.selected_starting_condition)
                elif selected_setting == 2:  # Type de carte
                    self.selected_map_type = self.cycle_option(MAP_TYPES, self.selected_map_type)
                elif selected_setting == 3:  # Retour
                    self.screen = GameScreen.MAIN_MENU

    def cycle_option(self, options, current_option):
        """Cycle through a list of options."""
        options_list = list(options)
        current_index = options_list.index(current_option)
        next_index = (current_index + 1) % len(options_list)
        return options_list[next_index]

    def gameplay_loop(self, stdscr):
        """Boucle principale pour le gameplay."""
        curses.curs_set(0)  # Cacher le curseur
        #stdscr.nodelay(True)  # Ne pas bloquer sur l'entrée utilisateur

        while self.screen == GameScreen.GAMEPLAY and self.running:
            stdscr.clear()
            self.update_units()
            self.render_map(stdscr)
            
            stdscr.refresh()

            key = stdscr.getch()
            move_speed = 1

            
            if key == curses.KEY_F12:
                # Switch to Pygame view
                subprocess.Popen([sys.executable, "main.py"])
                self.running = False

            if key == ord('Z'):
                move_speed = 5

            if key == ord('z') or key == curses.KEY_UP:
                self.camera_y = max(0, self.camera_y - move_speed)
            elif key == ord('s') or key == curses.KEY_DOWN:
                self.camera_y = min(self.game_state.carte.hauteur - 20, self.camera_y + move_speed)
            elif key == ord('q') or key == curses.KEY_LEFT:
                self.camera_x = max(0, self.camera_x - move_speed)
            elif key == ord('d') or key == curses.KEY_RIGHT:
                self.camera_x = min(self.game_state.carte.largeur - 40, self.camera_x + move_speed)
            elif key == ord('p'):
                self.screen = GameScreen.PAUSE
                self.pause_menu(stdscr)
            elif key == ord('m'):
                self.screen = GameScreen.MAIN_MENU
    
    
    
    def update_units(self):
        """Met à jour les positions des unités."""
        for unit in self.game_state.model['units']:
            unit.update()
    

    def render_map(self, stdscr):
        """Affiche la carte dans le terminal avec la caméra."""
        carte = self.game_state.carte
        units = self.game_state.model['units']
        buildings = self.game_state.model['buildings']
        
        # Initialiser les couleurs de curses
        curses.start_color()
        curses.init_pair(1, curses.COLOR_MAGENTA, curses.COLOR_BLACK)  # Violet pour les bâtiments
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)    # Vert pour les unités
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)   # Jaune pour les ressources
        
        # Désactiver l'écho des touches et masquer le curseur
        curses.noecho()
        curses.curs_set(0)
        
        # Créer une grille vide
        grille = [[("  ", curses.color_pair(0)) for _ in range(carte.largeur)] for _ in range(carte.hauteur)]

        def find_free_position(x, y):
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < carte.largeur and 0 <= ny < carte.hauteur and grille[ny][nx] == ("  ", curses.color_pair(0)):
                    return nx, ny
            return x, y  
            
        # Placer les ressources sur la carte (sans afficher les types de terrain)
        for y in range(len(carte.grille)):
            for x in range(len(carte.grille[0])):
                if carte.grille[y][x].resource:
                    rx, ry = find_free_position(x, y)
                    grille[ry][rx] = (carte.grille[y][x].resource.symbol, curses.color_pair(3))

        # Placer les bâtiments sur la grille
        for building in buildings:
            x, y = building.pos
            width_b, height_b = building.size  # Taille du bâtiment (largeur, hauteur)
            symbol = building.symbol

            # Remplir toutes les cases occupées par le bâtiment
            for i in range(height_b):
                for j in range(width_b):
                    bx, by = x + j, y + i  # Calcul des coordonnées
                    if 0 <= bx < carte.largeur and 0 <= by < carte.hauteur:
                        grille[by][bx] = (symbol, curses.color_pair(1))
            
            if width_b == 4 and height_b == 4:
                for i in range(-1, 5):
                    for j in range(-1, 5):
                        bx, by = x + j, y + i
                        if 0 <= bx < carte.largeur and 0 <= by < carte.hauteur:
                            if i == -1 or i == 4 or j == -1 or j == 4:
                                grille[by][bx] = ("#", curses.color_pair(1))

        # Placer les unités sur la grille
        for unit in units:
            x, y = unit.position
            symbol = unit.symbol
            ux, uy = find_free_position(x, y)
            if 0 <= x < carte.largeur and 0 <= y < carte.hauteur:
                grille[uy][ux] = (symbol, curses.color_pair(2))

        # Obtenir la taille de l'écran
        height, width = stdscr.getmaxyx()

        # Calculer la taille visible de la grille en fonction de la taille de l'écran
        visible_height = min(40, height - 1)  # 20 lignes visibles ou moins si l'écran est plus petit
        visible_width = min(50, width // 2)   # 40 colonnes visibles ou moins si l'écran est plus petit

        # Effacer l'écran avant de redessiner
        stdscr.clear()

        # Afficher la grille avec la caméra
        visible_rows = grille[self.camera_y:self.camera_y + visible_height]
        for row in visible_rows:
            for cell in row[self.camera_x:self.camera_x + visible_width]:
                symbol, color = cell
                stdscr.addstr(" "+symbol+" ", color)
            stdscr.addstr("\n")

        # Rafraîchir l'écran pour afficher les changements
        stdscr.refresh()

    def run(self):
        curses.wrapper(self.main_menu)
