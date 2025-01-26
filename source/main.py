import pygame
from models.Resources.map import Map
from models.Resources.tile import Tile
from views.game_view import GameView
from views.assets_manager import AssetManager

def initialize_game() -> tuple:
    """Initialize the game and return essential components."""
    pygame.init()
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 30)
    
    screen_info = pygame.display.Info()
    SCREEN_WIDTH = screen_info.current_w
    SCREEN_HEIGHT = screen_info.current_h
    TILE_SIZE = 70
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Age of Empires Pygame test')

    return screen, clock, font, TILE_SIZE

def main():
    screen, clock, font, TILE_SIZE = initialize_game()
    asset_manager = AssetManager()
    game_view = GameView(screen, TILE_SIZE, asset_manager)
    game_map = Map(120, 120)
    
    camera_x, camera_y = 0, 0
    running = True
    while running:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        game_view.render_map(game_map, camera_x, camera_y)
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()