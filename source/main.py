import pygame
from views.game_view import GameView
from views.assets_manager import AssetManager
from views.camera import Camera
from models.game import Game
from models.Buildings.farm import Farm
from models.Buildings.house import House
from models.Buildings.camp import Camp
from models.Buildings.keep import Keep
from models.Units.archer import Archer
from models.Units.horseman import Horseman
from models.Units.swordsman import Swordsman
from models.Units.villager import Villager
import random
import threading

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
    pygame.display.set_caption('Age of Empires Pygame test')

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
    game = Game(60, 60, "Moyenne", "default")
    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, game.map.width, game.map.height)

    game.map.add_resources(game.map_type)
    
    stop_event = threading.Event()
    player1_thread = threading.Thread(target=player_play_turn, args=(game.players[0], game, clock, stop_event))
    player2_thread = threading.Thread(target=player_play_turn, args=(game.players[1], game, clock, stop_event))

    player1_thread.start()
    player2_thread.start()

    running = True
    while running:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        camera.handle_input()
        camera_x, camera_y = camera.scroll.x, camera.scroll.y

        game_view.render_game(game.map, camera_x, camera_y, clock, game.players)
        game_view.render_minimap(game.map, game.players)

        pygame.display.flip()
        
        clock.tick(60)

        if game.check_game_over():
            running = False
            print("Game Over")
    
    stop_event.set()
    player1_thread.join()
    player2_thread.join()
    pygame.quit()

if __name__ == "__main__":
    main()