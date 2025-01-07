from enum import Enum

class Type(Enum):
    Wood = "Wood"
    Food = "Food"
    Gold = "Gold"
    Town_Hall = "Town_Hall"
    House = "House"
    Camp = "Camp"
    Farm = "Farm"
    Barracks = "Barracks"
    Stable = "Stable"
    Archery_Range = "Archery_Range"
    Keep = "Keep"


class Tile:
    def __init__(self, pos, tile_type):
        """
        Initializes a tile with a position and type.

        :param pos: Tuple (x, y) representing the position of the tile.
        :param tile_type: Type of the tile (Type Enum).
        """
        self.pos = pos  # Position of the tile (x, y)
        self.type = tile_type  # Type (Wood, Food, etc.)
        """pourquoi une liste sachant que sur une tuile on ne stocke qu'un élément ?"""
        self.units = []

    def get_pos(self):
        return self.pos

    def get_type(self):
        return self.type
    
    def add_unit(self, unit):
        self.units.append(unit)
    
    def remove_unit(self, unit):
        if unit in self.units:
            self.units.remove(unit)
            
    def has_units(self):
        return len(self.units) > 0
            
    def display_units(self):
        """
        Returns a string representation of the units on the tile.
        """
        if self.has_units():
            # Display all unit symbols joined together, or customize how units are shown.
            return "".join(self.units[0].symbol)
        return None
