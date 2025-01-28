import pygame
from views.game_view import GameView
from views.assets_manager import AssetManager
from views.camera import Camera
from models.game import Game, MAP_SIZES
from models.Buildings.farm import Farm
from models.Buildings.barrack import Barrack
import threading
from views.menu import main_menu, pause_menu, settings_menu, load_menu, save_menu  # Importer les fonctions de menu

def initialize_game() -> tuple:
    """Initialize the game and return essential components."""
    pygame.init()
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 30)
    
    screen_info = pygame.display.Info()
    SCREEN_WIDTH = screen_info.current_w
    SCREEN_HEIGHT = screen_info.current_h
    TILE_SIZE = 64
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Age of Empires Pygame')

    return screen, clock, font, TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT

def player_play_turn(player, game, clock, stop_event):
    while not stop_event.is_set():
        try:
            player.play_turn(game, clock)
        except ValueError as e:
            print(e)
        except Exception as e:
            print(f"Exception in player_play_turn: {e}")

def main():
    screen, clock, font, TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT = initialize_game()
    asset_manager = AssetManager()
    game_view = GameView(screen, TILE_SIZE, asset_manager)
    
    # Afficher le menu principal
    menu_action = main_menu(screen, None)
    if menu_action == "quit":
        pygame.quit()
        return
    elif menu_action == "load":
        save_file = load_menu(screen)
        if save_file != "quit":
            game = Game.load_game(save_file)
        else:
            pygame.quit()
            return
    elif isinstance(menu_action, dict) and menu_action.get("action") == "start":
        map_size = menu_action.get("map_size", "Medium")
        map_type = menu_action.get("map_type", "default")
        starting_condition = menu_action.get("starting_condition", "Maigre")
        width, height = MAP_SIZES[map_size]
        game = Game(width, height, starting_condition, map_type)
    else:
        game = Game(200, 200, "Moyenne", "default")

    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, game.map.width, game.map.height)

    game.map.add_resources(game.map_type)
    
    stop_event = threading.Event()

    player1_thread = threading.Thread(target=player_play_turn, args=(game.players[0], game, clock, stop_event))
    player2_thread = threading.Thread(target=player_play_turn, args=(game.players[1], game, clock, stop_event))

    player1_thread.start()
    player2_thread.start()

    running = True
    paused = False
    while running:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = not paused
                    if paused:
                        pause_action = pause_menu(screen, game)
                        if pause_action == "quit":
                            running = False
                        elif pause_action == "main_menu":
                            menu_action = main_menu(screen, None)
                            if menu_action == "quit":
                                running = False
                            elif isinstance(menu_action, dict) and menu_action.get("action") == "start":
                                map_size = menu_action.get("map_size", "Medium")
                                map_type = menu_action.get("map_type", "default")
                                starting_condition = menu_action.get("starting_condition", "Maigre")
                                width, height = MAP_SIZES[map_size]
                                game = Game(width, height, starting_condition, map_type)
                                game.players[0].add_building("Farm", position=(5, 5))  # Ajout d'une ferme pour le joueur 1
                                camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, game.map.width, game.map.height)
                                game.map.add_resources(game.map_type)
                                player1_thread = threading.Thread(target=player_play_turn, args=(game.players[0], game, clock, stop_event))
                                player2_thread = threading.Thread(target=player_play_turn, args=(game.players[1], game, clock, stop_event))
                                player1_thread.start()
                                player2_thread.start()
                                paused = False
                            elif isinstance(pause_action, dict) and pause_action.get("action") == "load":
                                game = Game.load_game(pause_action.get("file"))
                                camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, game.map.width, game.map.height)
                                player1_thread = threading.Thread(target=player_play_turn, args=(game.players[0], game, clock, stop_event))
                                player2_thread = threading.Thread(target=player_play_turn, args=(game.players[1], game, clock, stop_event))
                                player1_thread.start()
                                player2_thread.start()
                                paused = False
                            else:
                                paused = False
                elif event.key == pygame.K_F12:
                    save_filename = save_menu(screen)
                    if save_filename:
                        game.save_game(save_filename)

                elif event.key == pygame.K_p:
                        game_view.show_resource_ui = not game_view.show_resource_ui # Modifier la variable si "p" est pressé
                elif event.key == pygame.K_m:
                        game_view.show_minimap = not game_view.show_minimap  # Modifier la variable si "m" est pressé

        if not paused:
            camera.handle_input()
            camera_x, camera_y = camera.scroll.x, camera.scroll.y

        game_view.render_game(game.map, camera_x, camera_y, clock, game.players)

        pygame.display.flip()

        clock.tick(150)
    
    stop_event.set()
    player1_thread.join()
    player2_thread.join()
    pygame.quit()

if __name__ == "__main__":
    main()