from models.Buildings.building import Building
from models.Resources.resource_type import ResourceType
import time

class ArcheryRange(Building):
    def __init__(self, position=(0, 0)):
        super().__init__(name="Archery Range", build_time=50, hp=500, size=(3, 3), position=position, symbol="A")
        self.offset_x = 100
        self.offset_y = 100
        self.cost = {ResourceType.WOOD: 175}

    def spawn_archer(self, map, player):
        from models.Units.archer import Archer  # Local import to avoid circular import
        if player.resources[ResourceType.WOOD] < 25 or player.resources[ResourceType.GOLD] < 45:
            raise ValueError("Not enough resources to create an Archer")
        time.sleep(35)  # Simulate 35 seconds spawn time
        spawn_position = self._find_spawn_position(map)
        if spawn_position:
            archer = Archer(position=spawn_position)
            map.add_unit(archer)
            player.add_unit(archer)
            player.resources[ResourceType.WOOD] -= 25
            player.resources[ResourceType.GOLD] -= 45
        else:
            raise ValueError("No valid spawn position available")

    def _find_spawn_position(self, map):
        for dx in range(-1, self.size[0] + 1):
            for dy in range(-1, self.size[1] + 1):
                x, y = self.position[0] + dx, self.position[1] + dy
                if 0 <= x < map.width and 0 <= y < map.height:
                    tile = map.get_tile(x, y)
                    if tile.occupant is None or isinstance(tile.occupant, list):
                        return (x, y)
        return None
