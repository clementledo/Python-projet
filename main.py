import pygame
from menu import main_menu, pause_menu
from game_state import GameState

# Constants en haut du fichier
TILE_SIZE = 50
SAVE_FILE = "save_game.pkl"

def initialize_display():
    """Configure l'affichage du jeu"""
    screen_info = pygame.display.Info()
    screen = pygame.display.set_mode(
        (screen_info.current_w, screen_info.current_h), 
        pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF
    )
    pygame.display.set_caption('Age of Empires Pygame Clone')
    return screen, screen_info.current_w, screen_info.current_h

def main():
    # Initialize Pygame
    pygame.init()
    
    # Horloge pour gérer les FPS
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 30)

    screen, SCREEN_WIDTH, SCREEN_HEIGHT = initialize_display()
    game_state = GameState()
    current_screen = "main_menu"
    running = True

    while running:
        try:
            if current_screen == "main_menu":
                current_screen = handle_main_menu(screen, game_state, SCREEN_WIDTH, SCREEN_HEIGHT)
            elif current_screen == "gameplay":
                current_screen = handle_gameplay(game_state, clock, font, screen)
            elif current_screen == "pause_menu":
                current_screen = handle_pause_menu(screen, game_state)
            elif current_screen == "quit":
                running = False
        except Exception as e:
            print(f"Erreur: {e}")
            current_screen = "main_menu"

    # Quit Pygame
    pygame.quit()

def handle_main_menu(screen, game_state, width, height):
    """Gère le menu principal"""
    action = main_menu(screen, game_state)
    if action == "start":
        game_state.start_new_game(screen, width, height, TILE_SIZE)
        return "gameplay"
    elif action == "load_game":
        try:
            game_state.load_state(SAVE_FILE)
            return "gameplay"
        except FileNotFoundError:
            print("Aucune sauvegarde trouvée!")
    elif action == "quit":
        return "quit"
    return "main_menu"

def handle_gameplay(game_state, clock, font, screen):
    """Gère le gameplay"""
    running = game_state.controller.handle_input()

    # Check if the user paused the game
    if game_state.controller.paused:
        return "pause_menu"

    if not running:
        return "quit"

    game_state.controller.update()

    # Clear screen
    screen.fill((0, 0, 0))

    # Render game elements
    game_state.view.render_map(game_state.carte, game_state.controller.camera_x, game_state.controller.camera_y, game_state.controller.zoom_level)
    game_state.view.render_units(game_state.model['units'], game_state.controller.camera_x, game_state.controller.camera_y, game_state.controller.zoom_level, game_state.controller.selected_unit)
    game_state.view.render_buildings(game_state.model['buildings'], game_state.controller.camera_x, game_state.controller.camera_y, game_state.controller.zoom_level)
    game_state.view.render_minimap(game_state.carte, game_state.controller.camera_x, game_state.controller.camera_y, game_state.controller.zoom_level, game_state.model['units'],game_state.model['buildings'])

    game_state.show_fps(clock=clock,font=font,screen=screen)

    # Update display
    pygame.display.flip()

    return "gameplay"

def handle_pause_menu(screen, game_state):
    """Gère le menu pause"""
    action = pause_menu(screen, game_state)
    if action == "resume":
        # Resume the game
        game_state.controller.paused = False
        return "gameplay"
    elif action == "save":
        # Save the game
        game_state.save_state(SAVE_FILE)
        print("Game saved!")
    elif action == "load":
        # Load the game
        try:
            game_state.load_state(SAVE_FILE)
            print("Game loaded!")
        except FileNotFoundError:
            print("No saved game found!")
    elif action == "main_menu":
        # Go to the main menu
        return "main_menu"
    elif action == "quit":
        # Quit the game
        return "quit"
    return "pause_menu"

if __name__ == "__main__":
    main()
