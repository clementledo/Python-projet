from .tile import Tile

class Resource(Tile):
    def __init__(self, pos, resource_type, symbol, quantity):
        super().__init__(pos, resource_type)
        self.symbol = symbol  # Symbol representation (e.g., 'W' for wood)
        self.quantity = quantity  # Quantity of resource available

    def get_symbol(self):
        return self.symbol

    def get_quantity(self):
        return self.quantity

    def reduce_quantity(self, amount):
        self.quantity = max(0, self.quantity - amount)  # Prevents negative quantity
        
    def collect(self, amount):
        if amount <= self.quantity:
            self.reduce_quantity(amount)
        else:
            print("Pas assez de ressources")

