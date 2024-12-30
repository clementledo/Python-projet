from models.map import Map
from models.units.villager import Villager
from models.units.archer import Archer
from models.units.horseman import  Horseman
from models.Buildings import *
from game_state import GameState
from views.terminal_view import TerminalView

def main():
    # Créer une nouvelle partie
    tiles_x = 10
    tiles_y = 10
    game_state = GameState()
    game_state.start_new_game(None, tiles_x, tiles_y, tile_size=1,use_terminal_view=True)

    
    # Charger la vue terminale
    terminal_view = TerminalView(game_state)

    # Lancer le jeu
    terminal_view.run()

if __name__ == "__main__":
    main()
