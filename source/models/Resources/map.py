from .tile import Tile

class Map:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[Tile(x, y) for x in range(width)] for y in range(height)]

    def get_tile(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x]
        else:
            raise ValueError("Coordinates out of bounds")

    def set_tile(self, x, y, tile):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x] = tile
        else:
            raise ValueError("Coordinates out of bounds")
