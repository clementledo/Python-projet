import math
import random
from models.Resources.Tile import Tile
from models.Resources.Resource import Resource

class Map:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[Tile(x, y) for x in range(width)] for y in range(height)]
        self.generer_aleatoire()
        """self.all_unit = []"""

    def place_tile(self, x, y):
        self.grid[y][x] = Tile((x, y))

    def get_tile(self, x, y):
        return self.grid[y][x]
    
    def is_within_bounds(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def is_tile_occupied(self, x, y):
        return self.grid[y][x].resource != None and self.grid[y][x].occupant != None

    
    def is_area_free(self, top_left_x, top_left_y, width, height):
        for i in range(width):
            for j in range(height):
                if not self.is_within_bounds(top_left_x + i, top_left_y + j) or self.is_tile_occupied(top_left_x + i, top_left_y + j):
                    return False
        return True
    
    def place_building(self, building):
        """
        Place a building on the map
        """
        x, y = building.position

        # Check if the space is free and within bounds
        if not self.is_area_free(x, y, 1, 1):
            raise ValueError("Building can't be placed: space is either occupied or out of bounds.")

        self.grid[y][x].occupant = building  

        #self.buildings_on_map.append(building)
        print(f"Placed {building.__class__.__name__} at position ({x}, {y}).")

    def remove_building(self, building):
        """Remove a building from the map, freeing up its area."""
        x, y = building.position
        self.grid[j][i].occupant = None
    
    def update_unit_position(self, unit, old_position, new_position):
        """
        Updates the map by moving a unit from one tile to another.
        :param unit: The unit to move.
        :param old_position: Tuple (x, y) of the unit's previous position.
        :param new_position: Tuple (x, y) of the unit's new position.
        """
        x, y = old_position 
        self.grid[y][x].occupant = None
        x, y = new_position
        self.grid[y][x].occupant = unit
        unit.destination = new_position
        unit.update()
        
        """
        if old_position:
            old_tile = self.get_tile(*old_position)
            old_tile.remove_unit(unit)  # Remove the unit from the old tile
        
        new_tile = self.get_tile(*new_position)
        new_tile.add_unit(unit)  # Add the unit to the new tile
        """

    def create_forest(self, nb_tree, pos_x, pos_y):
        radius = int(math.sqrt(nb_tree)) 

        for i in range(pos_x, pos_x + radius):
            for j in range(pos_y, pos_y + radius):    
                # Check if the position is within the map boundaries
                if 0 <= i < self.height and 0 <= j < self.width:  # Ensure the position is valid 
                    self.grid[i][j].ressource = Resource("Wood", [100, 0, 0])

    def create_mine(self, nb_gold, pos_x, pos_y):
        radius = int(math.sqrt(nb_gold))
        for i in range(pos_x, pos_x + radius):
            for j in range(pos_y, pos_y + radius):    
                # Check if the position is within the map boundaries
                if 0 <= i < self.height and 0 <= j < self.width:  # Ensure the position is valid
                    self.grid[i][j].ressource = Resource("Gold", [0, 800, 0])

    def generer_aleatoire(self, nb_wood = 500, nb_gold = 100, type = 1):
        if type == 1:
            self.create_mine(nb_gold, self.width//2 - 5, self.height//2 - 5)
        else:
            base_mines = nb_gold//10
            min_mines = int(base_mines*0.8)
            max_mines = int(base_mines*1.2)
            for i in range(10):
                nb_mine = random.randint(min_mines, max_mines)
                pos_x = random.randint(0, self.width - int(math.sqrt(nb_mine)))
                pos_y = random.randint(0, self.height - int(math.sqrt(nb_mine)))
                self.create_mine(nb_mine, pos_x, pos_y)  

        base_trees = nb_wood // 20
        min_trees = int(base_trees*0.8)  # Allow slight variation
        max_trees = int(base_trees*1.2)        
    
        for i in range(20):
        # Randomly choose the number of trees for each forest (up to remaining trees)
            nb_tree = random.randint(min_trees, max_trees)  # Ensure we leave enough for the other forests
            trees_left -= nb_tree  # Deduct the chosen number of trees from remaining trees
        
        # Randomly choose a position on the map for the current forest
            pos_x = random.randint(0, self.width - int(math.sqrt(nb_tree)))
            pos_y = random.randint(0, self.height - int(math.sqrt(nb_tree)))
        
        # Create the forest at the chosen position
            self.create_forest(nb_tree, pos_x, pos_y)  

        
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
        
