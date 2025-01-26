import pygame
from models.Resources.terrain_type import Terrain_type
from models.Units.status import Status
from models.Units.villager import Villager
from models.Units.unit import Unit

class GameView:
    def __init__(self, screen, tile_size=50, asset_manager=None):
        self.screen = screen
        self.tile_size = tile_size
        self.asset_manager = asset_manager
        self.unit_sprites = {}
        self.building_sprites = {}
        
        self.font = pygame.font.SysFont('Arial', 24)
        self.decorations = []
        self.decorations_generated = False
        self.sprite_cache = {}
        self.viewport_width = screen.get_width()
        self.viewport_height = screen.get_height()
        self.dirty_rects = []
        
        self.unit_animation_frames = {}  # Store animation frame indexes for all units
        self.animation_speed = 5 # Default animation speed
        self.standing_animation_speed = 15 # Animation speed for standing
        self.animation_tick = 0
        self.unit_animation_ticks = {} # Store animation ticks for every unit
        self.animation_directions = {} # Store animation directions for every unit
        self.unit_offsets = {} # Store offsets for each unit

    def world_to_screen(self, x, y, camera_x, camera_y):
        tile_width = self.tile_size * 2
        tile_height = self.tile_size 
        iso_x = (x - y) * tile_width // 2 - camera_x
        iso_y = (x + y) * tile_height // 2 - camera_y
        return iso_x, iso_y

    def screen_to_world(self, screen_x, screen_y, camera_x, camera_y):
        tile_width = self.tile_size * 2
        tile_height = self.tile_size
        screen_x -= self.viewport_width // 2
        screen_y -= self.viewport_height // 4
        x = ((screen_x + camera_x) // (tile_width // 2) + (screen_y + camera_y) // (tile_height // 2)) // 2
        y = ((screen_y + camera_y) // (tile_height // 2) - (screen_x + camera_x) // (tile_width // 2)) // 2
        return x, y
    
    def render_map(self, carte, camera_x, camera_y):
        base_textures = {
            Terrain_type.GRASS: self.asset_manager.terrain_textures[Terrain_type.GRASS],
        }
        tile_width = self.tile_size * 2
        tile_height = self.tile_size
        textures = {
            terrain: pygame.transform.scale(texture, (tile_width, tile_height))
            for terrain, texture in base_textures.items()
        }
        screen_width, screen_height = self.screen.get_size()
        map_width = len(carte.grid[0])
        map_height = len(carte.grid)
        min_x, min_y = self.screen_to_world(0, 0, camera_x, camera_y)
        max_x, max_y = self.screen_to_world(screen_width, screen_height, camera_x, camera_y)
        min_x, min_y = int(min_x), int(min_y)
        max_x, max_y = int(max_x), int(max_y)
        padding_x = int(screen_width / tile_width)
        padding_y = int(screen_height / tile_height)
        min_x = max(min_x - padding_x, 0)
        min_y = max(min_y - padding_y, 0)
        max_x = min(max_x + padding_x, map_width - 1)
        max_y = min(max_y + padding_y, map_height - 1)

        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                tile = carte.get_tile(x, y)
                if not tile:
                    continue
                iso_x, iso_y = self.world_to_screen(x, y, camera_x, camera_y)
                terrain_texture = textures.get(tile.terrain_type, textures[Terrain_type.GRASS])
                self.screen.blit(terrain_texture, (iso_x, iso_y))
                iso_x, iso_y = self.world_to_screen(x, y, camera_x, camera_y)
                
                if tile.has_resource():
                    if tile.resource.is_wood():
                        tree_offset_y = tile_height // 0.47
                        tree_offset_x = tile_width // 2
                        resource_texture = self.asset_manager.wood_sprites['tree']
                        self.screen.blit(resource_texture, (iso_x - tree_offset_x, iso_y - tree_offset_y))
                    elif tile.resource.is_gold():
                        gold_offset_y = -tile_height // 2.8
                        resource_texture = self.asset_manager.gold_sprites['gold']
                        self.screen.blit(resource_texture, (iso_x + 0, iso_y + gold_offset_y))

                elif tile.is_occupied():
                    occupant = tile.occupant
                    if hasattr(occupant, 'size') and hasattr(occupant, 'name'):
                        if (x, y) == (occupant.position[0] + occupant.size[1] - 1, occupant.position[1] + occupant.size[1] - 1):
                            building_sprite = self.asset_manager.building_sprites.get(occupant.name)
                            if building_sprite:
                                iso_bx, iso_by = self.world_to_screen(occupant.position[0], occupant.position[1], camera_x, camera_y)
                                offset_x = occupant.offset_x
                                offset_y = occupant.offset_y
                                self.screen.blit(building_sprite, (iso_bx - offset_x, iso_by - offset_y))

                if tile.occupant:
                    occupant = tile.occupant
                    if isinstance(occupant, Unit):
                        self.render_units(occupant, carte, camera_x, camera_y)

    def render_units(self, unit, carte, camera_x, camera_y):
        """Render any unit on the map."""
        # Use interpolated position for smooth movement
        if unit.status == Status.WALKING and unit.path:
            next_x, next_y = unit.path[0]
            current_x, current_y = unit.position
            interp_x = current_x + (next_x - current_x) * unit.move_progress
            interp_y = current_y + (next_y - current_y) * unit.move_progress
            iso_x, iso_y = self.world_to_screen(interp_x, interp_y, camera_x, camera_y)
        else:
          iso_x, iso_y = self.world_to_screen(unit.position[0], unit.position[1], camera_x, camera_y)

        # Determine animation type based on unit status
        animation_type = 'standing'  # Default animation type
        if unit.status == Status.WALKING:
            animation_type = 'walking'
        elif unit.status == Status.ATTACKING:
            animation_type = 'building'
        
        # Get the correct animation frames
        animation_frames = self.asset_manager.get_villager_sprites(animation_type)
        if animation_frames:
            # Ensure frame index is initialized for this unit
            if unit not in self.unit_animation_frames:
                self.unit_animation_frames[unit] = {animation_type: 0}
            elif animation_type not in self.unit_animation_frames[unit]:
                self.unit_animation_frames[unit][animation_type] = 0

            # Ensure animation tick is initialized for this unit
            if unit not in self.unit_animation_ticks:
                self.unit_animation_ticks[unit] = {animation_type: 0}
            elif animation_type not in self.unit_animation_ticks[unit]:
                 self.unit_animation_ticks[unit][animation_type] = 0

            # Ensure animation direction is initialized for this unit
            if unit not in self.animation_directions:
                 self.animation_directions[unit] = {animation_type: 1}
            elif animation_type not in self.animation_directions[unit]:
                self.animation_directions[unit][animation_type] = 1
            
            # Ensure offset is initialized for this unit
            if unit not in self.unit_offsets:
                self.unit_offsets[unit] = { 'x' : 0, 'y' : 0}  # Default offsets
                if isinstance(unit, Villager):
                     self.unit_offsets[unit]['x'] = 0
                     self.unit_offsets[unit]['y'] = 20
                # You can add more condition here for other units
            
            
            frame_index = self.unit_animation_frames[unit][animation_type]
            current_frame = animation_frames[frame_index % len(animation_frames)]
           
            self.screen.blit(current_frame, (iso_x + self.unit_offsets[unit]['x'], iso_y - current_frame.get_height() // 2 + self.unit_offsets[unit]['y']))

            # Update animation frame for this unit
            animation_speed = self.animation_speed
            if animation_type == 'standing':
                animation_speed = self.standing_animation_speed

            self.unit_animation_ticks[unit][animation_type] += 1
            if self.unit_animation_ticks[unit][animation_type] >= animation_speed:
                self.unit_animation_frames[unit][animation_type] += self.animation_directions[unit][animation_type]
                self.unit_animation_ticks[unit][animation_type] = 0
                if self.unit_animation_frames[unit][animation_type] >= len(animation_frames) - 1:
                    self.animation_directions[unit][animation_type] = -1
                elif self.unit_animation_frames[unit][animation_type] <= 0:
                   self.animation_directions[unit][animation_type] = 1

    def render_game(self, carte, camera_x, camera_y, clock):
        self.render_map(carte, camera_x, camera_y)
        fps = clock.get_fps()
        fps_text = self.font.render(f"FPS: {int(fps)}", True, pygame.Color('white'))
        self.screen.blit(fps_text, (10, 10))
        self.dirty_rects = []