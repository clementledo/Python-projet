from .resource import Resource
from .tile import Type

class Wood(Resource):
    def __init__(self, pos, quantity=100):
        """
        Initializes a Wood resource.

        :param pos: Position of the wood resource.
        :param quantity: Quantity of wood available (default 100).
        """
        super().__init__(pos, Type.Wood, 'W', quantity)