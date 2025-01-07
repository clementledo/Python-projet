from .resource import Resource
from .tile import Type

class Food(Resource):
    def __init__(self, pos, quantity=300):
        """
        Initializes a Food resource.

        :param pos: Position of the food resource.
        :param quantity: Quantity of food available (default 300).
        """
        super().__init__(pos, Type.Food, 'F', quantity)