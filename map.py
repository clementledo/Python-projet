from resource.tile import Tile
from resource.tile import Type
class Map:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[Tile((x, y), None) for x in range(width)] for y in range(height)]
        self.all_unit = []

    def place_tile(self, x, y, tile_type):
        self.grid[y][x] = Tile((x, y), tile_type)

    def get_tile(self, x, y):
        return self.grid[y][x]
    
    def is_within_bounds(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def is_tile_occupied(self, x, y):
        return self.grid[y][x].type != None

    def is_area_free(self, top_left_x, top_left_y, width, height):
        for i in range(width):
            for j in range(height):
                if not self.is_within_bounds(top_left_x + i, top_left_y + j) or self.is_tile_occupied(top_left_x + i, top_left_y + j):
                    return False
        return True
    
    def place_building(self, building):
        """
        Place a building on the map, marking all the tiles it occupies.
        Buildings may occupy multiple tiles (e.g., Town Hall is 4x4).
        """
        x, y = building.position
        width, height = building.size

        # Check if the space is free and within bounds
        if not self.is_area_free(x, y, width, height):
            raise ValueError("Building can't be placed: space is either occupied or out of bounds.")

        # Mark the tiles as occupied by the building
        for i in range(width):
            for j in range(height):
                self.grid[y + j][x + i].type = building.building_type  # Mark the grid with the building reference

        #self.buildings_on_map.append(building)
        print(f"Placed {building.__class__.__name__} at position ({x}, {y}).")

    def remove_building(self, building):
        """Remove a building from the map, freeing up its area."""
        x, y = building.position
        width, height = building.size

        # Mark the area as free
        for i in range(x, x + width):
            for j in range(y, y + height):
                if self.is_within_bounds(i, j):
                    self.grid[j][i].type = None
    
    def update_unit_position(self, unit, old_position, new_position):
        """
        Updates the map by moving a unit from one tile to another.
        :param unit: The unit to move.
        :param old_position: Tuple (x, y) of the unit's previous position.
        :param new_position: Tuple (x, y) of the unit's new position.
        """
        if old_position:
            old_tile = self.get_tile(*old_position)
            old_tile.remove_unit(unit)  # Remove the unit from the old tile
        
        new_tile = self.get_tile(*new_position)
        new_tile.add_unit(unit)  # Add the unit to the new tile


    def display(self):
        """
        Displays a simple text-based representation of the map.
        """
        for row in self.grid:
            row_str = ""
            for tile in row:
                if tile.has_units():
                    row_str += tile.display_units() + " "  # Display unit symbol if present
                elif tile.type:
                    row_str += tile.type.name[0] + " "  # Display first letter of tile type
                else:
                    row_str += ". "  # Empty tile
            print(row_str)
        print()    
        