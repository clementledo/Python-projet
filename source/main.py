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
from models.Resources.tile import Tile
from models.Resources.resource import Resource
from models.Resources.resource_type import ResourceType

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

def main():
    screen, clock, font, TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT = initialize_game()
    asset_manager = AssetManager()
    game_view = GameView(screen, TILE_SIZE, asset_manager)
    game = Game(60, 60, "Marines", "default")
    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, game.map.width, game.map.height)
    
    house = House(position=(58, 0))
    game.map.add_building(house)

    camp = Camp(position=(54, 1))
    game.map.add_building(camp)

    # farm = Farm(position=(54, 0))   
    # game.map.add_building(farm)

    # ajouter un archer (unit)
    archer = Archer(position=(59, 2))
    game.map.add_unit(archer)

    # ajouter un horseman (unit)
    horseman = Horseman(position=(59, 3))
    game.map.add_unit(horseman)

    game.map.add_resources(game.map_type)
    a = 1
    
    running = True
    while running:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        camera.handle_input()
        camera_x, camera_y = camera.scroll.x, camera.scroll.y

        game_view.render_game(game.map, camera_x, camera_y, clock)

        pygame.display.flip()
        
        if a == 2:
            # Déplacer l'archer vers une nouvelle position
            unit = game.players[0].units[0]
            unit.move_adjacent_to_resource(game.map, ResourceType.GOLD)
            while unit.path:
                unit.update_position()
                game_view.render_game(game.map, camera_x, camera_y, clock)
                pygame.display.flip()
                clock.tick(60)
            a = 3  # Pour éviter de répéter le déplacement

        if a == 1:
            game.display()
            a = 2
        
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()