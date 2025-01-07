from .resource import Resource
from .tile import Type

class Gold(Resource):
    def __init__(self, pos, quantity=800):
        """
        Initializes a Gold resource.

        :param pos: Position of the gold resource.
        :param quantity: Quantity of gold available (default 800).
        """
        super().__init__(pos, Type.Gold, 'G', quantity)