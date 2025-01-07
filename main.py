import pygame
from views.menu import main_menu, pause_menu, settings_menu
from game_state import GameState

def main():
    
    # Initialize Pygame
    pygame.init()
    
    # Horloge pour gérer les FPS
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 30)

    # Screen setup
    screen_info = pygame.display.Info()
    SCREEN_WIDTH = screen_info.current_w
    SCREEN_HEIGHT = screen_info.current_h
    TILE_SIZE = 50  # Tile size for the game

    # Create fullscreen window
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
    pygame.display.set_caption('Age of Empires Pygame Clone')

    # Initialize game state
    game_state = GameState()

    # Variable to track the current screen (e.g., "main_menu", "gameplay", "pause")
    current_screen = "main_menu"
    running = True

    map_sizes = {
        "Small": (30, 30),
        "Medium": (75, 75),
        "Large": (120, 120)
    }

    while running:
        if current_screen == "main_menu":
            action = main_menu(screen, game_state)
            if isinstance(action, dict) and action["action"] == "start":
                map_size = map_sizes[action["map_size"]]
                game_state.start_new_game(
                    screen, 
                    map_size[0], 
                    map_size[1], 
                    TILE_SIZE,
                    map_type=action["map_type"]
                )
                current_screen = "gameplay"
            elif action == "load":
                try:
                    game_state.load_state("save_game.pkl")
                    current_screen = "gameplay"
                except FileNotFoundError:
                    print("No saved game found!")
            elif action == "quit":
                running = False

        elif current_screen == "settings":
            settings_result = settings_menu(screen)
            if settings_result == "back":
                current_screen = "main_menu"
            elif isinstance(settings_result, dict):
                if settings_result["action"] == "start":
                    map_size = map_sizes[settings_result["map_size"]]
                    game_state.start_new_game(screen, map_size[0], map_size[1], TILE_SIZE)
                    current_screen = "gameplay"
                elif settings_result["action"] == "quit":
                    running = False
          
        elif current_screen == "gameplay":

                # Handle gameplay
                running = game_state.controller.handle_input()

                # Check if the user paused the game
                if game_state.controller.paused:
                    current_screen = "pause_menu"
                    continue

                if not running:
                    break

                game_state.controller.update()

                # Clear screen
                screen.fill((0, 0, 0))

                # Render game elements
                game_state.view.render_map(game_state.carte, game_state.controller.camera_x, game_state.controller.camera_y, game_state.controller.zoom_level)
                game_state.view.render_units(game_state.model['units'], game_state.controller.camera_x, game_state.controller.camera_y, game_state.controller.zoom_level, game_state.controller.selected_unit)
                game_state.view.render_buildings(game_state.model['buildings'], game_state.controller.camera_x, game_state.controller.camera_y, game_state.controller.zoom_level)
                game_state.view.render_minimap(game_state.carte, game_state.controller.camera_x, game_state.controller.camera_y, game_state.controller.zoom_level, game_state.model['units'],game_state.model['buildings'])

                #game_state.controller.move_unit_to_town_center()
                game_state.show_fps(clock=clock,font=font,screen=screen)

                # Update display
                pygame.display.flip()

        elif current_screen == "pause_menu":
            # Show the pause menu and handle the result
            action = pause_menu(screen, game_state)
            if action == "resume":
                # Resume the game
                game_state.controller.paused = False
                current_screen = "gameplay"
            elif action == "save":
                # Save the game
                game_state.save_state("save_game.pkl")
                print("Game saved!")
            elif action == "load":
                # Load the game
                try:
                    game_state.load_state("save_game.pkl")
                    print("Game loaded!")
                except FileNotFoundError:
                    print("No saved game found!")
            elif action == "main_menu":
                # Go to the main menu
                current_screen = "main_menu"
            elif action == "quit":
                # Quit the game
                running = False

    # Quit Pygame
    pygame.quit()

if __name__ == "__main__":
    main()
