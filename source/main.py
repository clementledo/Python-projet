import pygame
from views.game_view import GameView
from views.assets_manager import AssetManager
from views.camera import Camera
from models.game import Game
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

def player_collect_resources(player, game_map, clock):
    while True:
        try:
            player.send_villager_to_collect(game_map, clock)
        except ValueError as e:
            print(e)
            break

def main():
    screen, clock, font, TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT = initialize_game()
    asset_manager = AssetManager()
    game_view = GameView(screen, TILE_SIZE, asset_manager)
    game = Game(60, 60, "Moyenne", "default")
    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, game.map.width, game.map.height)

    game.map.add_resources(game.map_type)
    
    player1_thread = threading.Thread(target=player_collect_resources, args=(game.players[0], game.map, clock))
    player2_thread = threading.Thread(target=player_collect_resources, args=(game.players[1], game.map, clock))

    player1_thread.start()
    player2_thread.start()

    running = True
    while running:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    game_view.show_resource_ui = not game_view.show_resource_ui # Modifier la variable si "p" est pressé
                if event.key == pygame.K_m:
                    game_view.show_minimap = not game_view.show_minimap  # Modifier la variable si "m" est pressé

        camera.handle_input()
        camera_x, camera_y = camera.scroll.x, camera.scroll.y

        game_view.render_game(game.map, camera_x, camera_y, clock, game.players)

        pygame.display.flip()

        clock.tick(150)
    
    pygame.quit()

if __name__ == "__main__":
    main()