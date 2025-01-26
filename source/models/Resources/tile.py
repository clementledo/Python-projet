from .resource import Resource

class Tile:
    def __init__(self, x, y, occupant=None, resource: Resource = None):
        self.x = x
        self.y
        self.occupant = occupant
        self.resource = resource

    def __repr__(self):
        return f"Tile(x={self.x}, y={self.y}, occupant={self.occupant}, resource={self.resource})"

    def is_occupied(self):
        return self.occupant is not None

    def has_resource(self):
        return self.resource is not None