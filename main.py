import pygame
from models.units.villager import Villager
from models.units.archer import Archer
from models.units.horseman import Horseman
from views.game_view import GameView
from controllers.game_controller import GameController
from models.map import Map

def main():
    # Initialize Pygame
    pygame.init()

    # Screen setup
    screen_info = pygame.display.Info()
    SCREEN_WIDTH = screen_info.current_w
    SCREEN_HEIGHT = screen_info.current_h
    TILE_SIZE = 50  # Increased tile size for better visibility

    # Create fullscreen window
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
    pygame.display.set_caption('Age of Empires Pygame Clone')

    # Calculate map size based on screen dimensions
    TILES_X = int(SCREEN_WIDTH / (TILE_SIZE * 2)) + 20
    TILES_Y = int(SCREEN_HEIGHT / TILE_SIZE) + 20

    # Create map
    carte = Map(TILES_X, TILES_Y)
    carte.generer_aleatoire(type_carte="ressources_generales")

    # Initialize units
    units = [
        Villager(15, 12, carte),
        Villager(3,26,carte),
        Archer(20, 12, carte),
        Horseman(20,15,carte)
    ]
    model = {'units': units}

    # Initialize view and controller
    view = GameView(screen, tile_size=TILE_SIZE)
    view.load_unit_sprite('Villager', 'assets/villager.png')
    view.load_unit_sprite('Archer', 'assets/archer.png')
    view.load_unit_sprite('Horseman', 'assets/horseman.png')
    view.generate_decorations(carte)

    controller = GameController(model, view, carte)

    # Main game loop
    running = True
    while running:
        # Handle input
        running = controller.handle_input()

        # Clear screen
        screen.fill((0, 0, 0))

        # Render game elements
        view.render_map(carte, controller.camera_x, controller.camera_y, controller.zoom_level)
        view.render_units(model['units'], controller.camera_x, controller.camera_y, controller.zoom_level)
        view.render_minimap(carte, controller.camera_x, controller.camera_y, controller.zoom_level,units)

        # Update display
        pygame.display.flip()

    # Quit Pygame
    pygame.quit()

if __name__ == "__main__":
    main()