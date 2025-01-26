import pygame
from models.Resources.map import Map
from views.game_view import GameView
from views.camera import Camera
from views.assets_manager import AssetManager
from main import initialize_game
from models.game import Game

def test_specific_resources():
    screen, clock, font, TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT = initialize_game()
    game = Game(50, 50, "Moyenne", "central_gold")  # Initialiser le jeu avec les paramètres spécifiés
    test_map = game.map
    asset_manager = AssetManager()
    game_view = GameView(screen, TILE_SIZE, asset_manager)
    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, test_map.width, test_map.height)
    running = True

    while running:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        camera.handle_input()
        camera_x, camera_y = camera.scroll.x, camera.scroll.y
        game_view.render_game(test_map, camera_x, camera_y, clock)
        pygame.display.flip()
        clock.tick(250)

    pygame.quit()

if __name__ == "__main__":
    test_specific_resources()