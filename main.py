import pygame
from views.menu import main_menu, pause_menu, settings_menu
from game_state import GameState
from views.game_view import GameView
from controllers.game_controller import GameController

def render_for_load(game_state, screen, TILE_SIZE):
    """Initialize rendering for loaded game"""
    game_state.screen = screen
    game_state.view = GameView(screen, TILE_SIZE)
    
    # Load all required sprites
    game_state.view.load_building_sprite('T', "assets/Buildings/Towncenter.png")
    game_state.view.load_unit_sprite('Villager', "assets/Sprites/Villager/Stand/Villagerstand001.png")
    
    # Initialize game controller with all components
    game_state.controller = GameController(game_state.model, game_state.view, game_state.carte, TILE_SIZE)
    game_state.controller.camera_x = game_state.camera_x
    game_state.controller.camera_y = game_state.camera_y
    game_state.controller.zoom_level = game_state.zoom_level
    
    # Initialize UI and resources
    #game_state.controller.initialize_ui()
   # game_state.controller.update_resource_display()
    
    # Ensure resource panel is visible
    game_state.view.show_resource_panel = True

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
    TILE_SIZE = 70  # Tile size for the game

    # Create fullscreen window
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
    pygame.display.set_caption('Age of Empires Pygame Clone')

    # Initialize game state with screen
    game_state = GameState(screen)

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
                    map_type=action["map_type"],
                    starting_condition=action["starting_condition"]
                )
                current_screen = "gameplay"
                pygame.event.clear()
            elif action == "load":
                try:
                    if game_state.load_state():
                        
                        render_for_load(game_state, screen, TILE_SIZE)
                        current_screen = "gameplay"
                        pygame.event.clear()
                    else:
                        print("Failed to load game state!")
                except Exception as e:
                    print(f"Error loading game: {e}")
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
                 # Update game state
                game_state.update_ai()

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
                game_state.view.generate_resources(game_state.carte)
                game_state.view.render_units(game_state.model['units'], game_state.controller.camera_x, game_state.controller.camera_y, game_state.controller.zoom_level, game_state.controller.selected_unit)
                game_state.view.render_buildings(game_state.model['buildings'], game_state.controller.camera_x, game_state.controller.camera_y, game_state.controller.zoom_level)
                
                game_state.view.render_minimap(game_state.carte, game_state.controller.camera_x, game_state.controller.camera_y, game_state.controller.zoom_level, game_state.model['units'],game_state.model['buildings'])

                game_state.controller.move_unit_to_town_center()
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
                # Save with incremental filename
                game_state.save_state()  # No filename - will auto-increment
                print("Game saved!")
            elif action == "load":
                
                try:
                    if game_state.load_state():  # No filename - will load latest
                        # Réinitialise les éléments nécessaires au rendu
                        render_for_load(game_state, screen, TILE_SIZE)

                        current_screen = "gameplay"
                        pygame.event.clear()
                    else:
                        print("Failed to load game state!")
                except FileNotFoundError:
                    print("No saved game found!")
                except Exception as e:
                    print(f"Error loading game: {e}")
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
