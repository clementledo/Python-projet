from type import Type

class Pos:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Pos(x={self.x}, y={self.y})"

class Tile:
    def __init__(self, pos: Pos, tile_type: Type):
        self.pos = pos
        self.type = tile_type

    def get_pos(self) -> Pos:
        return self.pos

    def get_type(self) -> Type:
        return self.type

    def __repr__(self):
        return f"Tile(pos={self.pos}, type={self.type})"
