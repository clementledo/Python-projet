import pygame
from views.menu import main_menu, pause_menu, settings_menu
from game_state import GameState
from views.game_view import GameView
from controllers.game_controller import GameController

# Constants
SCREEN_STATES = {
    'MAIN_MENU': 'main_menu',
    'GAMEPLAY': 'gameplay',
    'PAUSE': 'pause_menu',
    'SETTINGS': 'settings'
}

ACTIONS = {
    'RESUME': 'resume',
    'SAVE': 'save',
    'LOAD': 'load',
    'QUIT': 'quit',
    'MAIN_MENU': 'main_menu'
}

MAP_SIZES = {
    "Small": (30, 30),
    "Medium": (75, 75),
    "Large": (120, 120)
}

def handle_updates(game_state):
    game_state.update_ai()
    running = game_state.controller.handle_input()
    if running:
        game_state.controller.update()
        game_state.controller.move_unit_to_town_center()
    return running

def handle_rendering(game_state, screen, clock, font):
    game_state.view.render_game(game_state, screen, clock, font)

def handle_settings_menu(screen, game_state, TILE_SIZE):
    """Handle settings menu logic"""
    settings_result = settings_menu(screen)
    if settings_result == "back":
        return SCREEN_STATES['MAIN_MENU']
    elif isinstance(settings_result, dict):
        if settings_result["action"] == "start":
            map_size = MAP_SIZES[settings_result["map_size"]]
            game_state.start_new_game(screen, map_size[0], map_size[1], TILE_SIZE)
            return SCREEN_STATES['GAMEPLAY']
        elif settings_result["action"] == "quit":
            return None
    return SCREEN_STATES['SETTINGS']

def initialize_game() -> tuple:
    """Initialize the game and return essential components."""
    pygame.init()
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 30)
    
    screen_info = pygame.display.Info()
    SCREEN_WIDTH = screen_info.current_w
    SCREEN_HEIGHT = screen_info.current_h
    TILE_SIZE = 70
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
    pygame.display.set_caption('Age of Empires Pygame Clone')
    
    game_state = GameState(screen)
    return screen, game_state, clock, font, TILE_SIZE

def handle_main_menu(screen, game_state, TILE_SIZE) -> str:
    """Handle the main menu logic."""
    action = main_menu(screen, game_state)
    if isinstance(action, dict) and action["action"] == "start":
        map_size = MAP_SIZES[action["map_size"]]
        game_state.start_new_game(
            screen, 
            map_size[0], 
            map_size[1], 
            TILE_SIZE,
            map_type=action["map_type"],
            starting_condition=action["starting_condition"]
        )
        pygame.event.clear()
        return SCREEN_STATES['GAMEPLAY']
    elif action == "load":
        return handle_load_game(game_state, screen, TILE_SIZE)
    elif action == "quit":
        return ACTIONS['QUIT']
    return SCREEN_STATES['MAIN_MENU']

def handle_load_game(game_state, screen, TILE_SIZE) -> str:
    """Handle loading a game state."""
    try:
        if game_state.load_state(game_state.get_latest_save()):
            game_state.initialize_game_components( screen, TILE_SIZE)
            pygame.event.clear()
            return SCREEN_STATES['GAMEPLAY']
        else:
            print("Failed to load game state!")
    except Exception as e:
        print(f"Error loading game: {e}")
    return SCREEN_STATES['MAIN_MENU']

def handle_pause_menu(screen, game_state, TILE_SIZE) -> tuple[str, bool]:
    """Handle pause menu logic."""
    action = pause_menu(screen, game_state)
    
    if action == ACTIONS['RESUME']:
        game_state.controller.paused = False
        return SCREEN_STATES['GAMEPLAY'], True
        
    elif action == ACTIONS['SAVE']:
        try:
            game_state.save_state()
            print("Game saved successfully!")
        except Exception as e:
            print(f"Error saving game: {e}")
        return SCREEN_STATES['PAUSE'], True
        
    elif action == ACTIONS['LOAD']:
        try:
            if game_state.load_state(game_state.get_latest_save()):
                game_state.initialize_game_components( screen, TILE_SIZE)
                pygame.event.clear()
                return SCREEN_STATES['GAMEPLAY'], True
            else:
                print("Failed to load game state!")
        except Exception as e:
            print(f"Error loading game: {e}")
        return SCREEN_STATES['PAUSE'], True
        
    elif action == ACTIONS['MAIN_MENU']:
        return SCREEN_STATES['MAIN_MENU'], True
        
    elif action == ACTIONS['QUIT']:
        return SCREEN_STATES['PAUSE'], False
        
    return SCREEN_STATES['PAUSE'], True

def main():
    screen, game_state, clock, font, TILE_SIZE = initialize_game()
    
    current_screen = SCREEN_STATES['MAIN_MENU']
    running = True

    while running:
        if current_screen == SCREEN_STATES['MAIN_MENU']:
            current_screen = handle_main_menu(screen, game_state, TILE_SIZE)
            if current_screen == ACTIONS['QUIT']:
                running = False

        elif current_screen == SCREEN_STATES['SETTINGS']:
            current_screen = handle_settings_menu(screen, game_state, TILE_SIZE)
            if current_screen is None:
                running = False

        elif current_screen == SCREEN_STATES['GAMEPLAY']:
            if game_state.controller.paused:
                current_screen = SCREEN_STATES['PAUSE']
                continue
                
            running = handle_updates(game_state)
            if not running:
                break
                
            handle_rendering(game_state, screen, clock, font)

        elif current_screen == SCREEN_STATES['PAUSE']:
            current_screen, running = handle_pause_menu(screen, game_state, TILE_SIZE)

    pygame.quit()

if __name__ == "__main__":
    main()
