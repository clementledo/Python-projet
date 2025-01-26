from .building import Building
import time

class TownCenter(Building):
    def __init__(self, position=(0, 0)):
        super().__init__(name="Town Centre", build_time=150, hp=1000, size=(4, 4), position=position, symbol="T")

    def spawn_villager(self, map):
        from models.Units.villager import Villager  # Local import to avoid circular import
        time.sleep(2.5)  # Simulate 25 seconds spawn time
        spawn_position = self._find_spawn_position(map)
        if spawn_position:
            villager = Villager(position=spawn_position)
            map.add_unit(villager)
        else:
            raise ValueError("No valid spawn position available")

    def _find_spawn_position(self, map):
        for dx in range(-1, self.size[0] + 1):
            for dy in range(-1, self.size[1] + 1):
                x, y = self.position[0] + dx, self.position[1] + dy
                if 0 <= x < map.width and 0 <= y < map.height:
                    tile = map.get_tile(x, y)
                    if tile.occupant is None:
                        return (x, y)
        return None