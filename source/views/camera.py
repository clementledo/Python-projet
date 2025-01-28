import pygame

class Camera:
    def __init__(self, width, height, grid_length_x, grid_length_y):
        self.width = width
        self.height = height
        self.scroll = pygame.Vector2(0, 0)
        self.speed = 10
        self.speed_max = 20
        self.base_tile_size = 64  # Base tile size
        self.TILE_SIZE = self.base_tile_size
        self.grid_length_x = grid_length_x
        self.grid_length_y = grid_length_y

        self.zoom = 1
        self.min_zoom = 0.0001
        self.max_zoom = 5.0
        
        self.update_limits()

    def update_limits(self):
        # Update tile size and limits based on zoom
        self.TILE_SIZE = int(self.base_tile_size * self.zoom)
        self.max_scroll_x = (self.grid_length_x * self.TILE_SIZE) - (self.width/2) + 100000
        self.max_scroll_y = (self.grid_length_y * self.TILE_SIZE) - (self.height/2) + 100000
        self.iso_offset_x = (abs(self.grid_length_x - self.grid_length_y) * self.TILE_SIZE) / 2
        self.iso_offset_y = (self.grid_length_y - 0.5 * self.grid_length_x) * self.TILE_SIZE

    def handle_input(self):
        keys = pygame.key.get_pressed()
        speed = self.speed_max if pygame.key.get_mods() & pygame.KMOD_SHIFT else self.speed

        # Handle zoom with mouse wheel
        for event in pygame.event.get(pygame.MOUSEBUTTONDOWN):
            if event.button == 4:  # Mouse wheel up
                self.zoom = min(self.zoom + 0.1, self.max_zoom)
                self.update_limits()
            elif event.button == 5:  # Mouse wheel down
                self.zoom = max(self.zoom - 0.1, self.min_zoom)
                self.update_limits()

        # Movement handling
        movement = pygame.Vector2(0, 0)
        if keys[pygame.K_z] or keys[pygame.K_DOWN]: movement.y += speed
        if keys[pygame.K_s] or keys[pygame.K_UP]: movement.y -= speed
        if keys[pygame.K_q] or keys[pygame.K_RIGHT]: movement.x += speed
        if keys[pygame.K_d] or keys[pygame.K_LEFT]: movement.x -= speed

        self.scroll += movement
        self.clamp_scroll()

    def clamp_scroll(self):
        # Utilisation des limites de la carte
        self.scroll.x = max(-self.max_scroll_x - self.iso_offset_x, min(self.scroll.x, self.max_scroll_x + self.iso_offset_x))
        self.scroll.y = max(-self.max_scroll_y - self.iso_offset_y, min(self.scroll.y, self.max_scroll_y + self.iso_offset_y))