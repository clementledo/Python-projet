from .resource import Resource

class Tile:
    def __init__(self, position, occupant=None, resource: Resource = None):
        self.position = position
        self.occupant = occupant
        self.resource = resource

    def __repr__(self):
        return f"Tile(position={self.position}, occupant={self.occupant}, resource={self.resource})"

    def is_occupied(self):
        return self.occupant is not None

    def has_resource(self):
        return self.resource is not None