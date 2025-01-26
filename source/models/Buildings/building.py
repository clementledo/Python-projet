class Building:
    def __init__(self, name, build_time, hp, size, position=(0, 0), walkable=False):
        self.name = name
        self.build_time = build_time
        self.hp = hp
        self.size = size
        self.position = position
        self.walkable = walkable

    def __repr__(self):
        return (f"Building(name={self.name}, build_time={self.build_time}, hp={self.hp}, "
                f"size={self.size}, position={self.position}, walkable={self.walkable})")

