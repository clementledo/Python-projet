from models.Units.unit import Unit
from models.Buildings.building import Building
from models.Buildings.towncenter import TownCenter
from models.Buildings.camp import Camp
from models.Buildings.farm import Farm
from models.Resources.tile import Tile
from models.Resources.resource_type import ResourceType
import math

class Villager(Unit):
    def __init__(self, position=(0, 0)):
        super().__init__(name="Villager", hp=25, attack=2, speed=0.8, position=position, symbol="v", animation_speed=4, offset_x=0, offset_y=20)
        self.carry_capacity = 20
        self.resource_collected = 0
        self.collection_rate = 25 #/ 60  # 25 resources per minute

    def build(self, building: Building, map, player, num_villagers=1):
        if not self._is_adjacent_to_building_site(building):
            self.move_adjacent_to_building_site(map, building)
        
        for resource, amount in building.cost.items():
            if player.resources.get(resource, 0) < amount:
                raise ValueError(f"Not enough {resource} to build {building.name}")

        nominal_time = building.build_time
        actual_time = 3 * nominal_time / (num_villagers + 2)
        if self._can_place_building(building, map):
            for _ in range(int(actual_time)):
                # Simulate building time
                print("building...")
                pass
            map.add_building(building)
            for resource, amount in building.cost.items():
                player.resources[resource] -= amount
        else:
            raise ValueError("Cannot place building at the specified location")

    def move_adjacent_to_building_site(self, map, building: Building):
        from queue import PriorityQueue
        import math

        def heuristic(a, b):
            return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

        def neighbors(pos):
            x, y = pos
            results = [(x + dx, y + dy) for dx in [-1, 0, 1] for dy in [-1, 0, 1] if dx != 0 or dy != 0]
            results = filter(lambda p: 0 <= p[0] < map.width and 0 <= p[1] < map.height, results)
            return results

        start = self.position
        goal_positions = [(building.position[0] + dx, building.position[1] + dy) for dx in [-1, 0, 1] for dy in [-1, 0, 1] if dx != 0 or dy != 0]
        goal_positions = [pos for pos in goal_positions if 0 <= pos[0] < map.width and 0 <= pos[1] < map.height]

        frontier = PriorityQueue()
        frontier.put((0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}

        while not frontier.empty():
            _, current = frontier.get()

            if current in goal_positions:
                goal = current
                break

            for next in neighbors(current):
                tile = map.get_tile(next[0], next[1])
                if tile.is_occupied() and not isinstance(tile.occupant, Unit) and not tile.occupant.walkable:
                    continue
                new_cost = cost_so_far[current] + heuristic(current, next)
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + heuristic(goal_positions[0], next)
                    frontier.put((priority, next))
                    came_from[next] = current
        else:
            raise ValueError("No valid path to target position or adjacent tiles")

        path = []
        current = goal
        while current != start:
            path.append(current)
            current = came_from[current]
        path.reverse()

        if path:
            self.position = path[-1]

    def move_adjacent_to_resource(self, map, resource_tile: Tile):
        from queue import PriorityQueue
        import math

        def heuristic(a, b):
            return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

        def neighbors(pos):
            x, y = pos
            results = [(x + dx, y + dy) for dx in [-1, 0, 1] for dy in [-1, 0, 1] if dx != 0 or dy != 0]
            results = filter(lambda p: 0 <= p[0] < map.width and 0 <= p[1] < map.height, results)
            return results

        start = self.position
        goal_positions = [(resource_tile.position[0] + dx, resource_tile.position[1] + dy) for dx in [-1, 0, 1] for dy in [-1, 0, 1] if dx != 0 or dy != 0]
        goal_positions = [pos for pos in goal_positions if 0 <= pos[0] < map.width and 0 <= pos[1] < map.height]

        frontier = PriorityQueue()
        frontier.put((0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}

        while not frontier.empty():
            _, current = frontier.get()

            if current in goal_positions:
                goal = current
                break

            for next in neighbors(current):
                tile = map.get_tile(next[0], next[1])
                if tile.is_occupied() and not isinstance(tile.occupant, Unit) and not tile.occupant.walkable:
                    continue
                new_cost = cost_so_far[current] + heuristic(current, next)
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + heuristic(goal_positions[0], next)
                    frontier.put((priority, next))
                    came_from[next] = current
        else:
            raise ValueError("No valid path to target position or adjacent tiles")

        path = []
        current = goal
        while current != start:
            path.append(current)
            current = came_from[current]
        path.reverse()

        if path:
            self.position = path[-1]

    def _is_adjacent_to_building_site(self, building: Building):
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                x, y = self.position[0] + dx, self.position[1] + dy
                if (x, y) == building.position:
                    return True
        return False

    def _can_place_building(self, building: Building, map):
        if building.position[0] + building.size[0] > map.width or building.position[1] + building.size[1] > map.height:
            return False
        for i in range(building.size[1]):
            for j in range(building.size[0]):
                if map.get_tile(building.position[0] + j, building.position[1] + i).occupant is not None or map.get_tile(building.position[0] + j, building.position[1] + i).has_resource():
                    return False
        return True

    def collect_resource(self, tile: Tile, map):
        if self._is_adjacent(tile) and tile.has_resource():
            amount = min(self.collection_rate, tile.resource.quantity, self.carry_capacity - self.resource_collected)
            self.resource_collected += amount
            print(f"{self} collected {amount} from {tile}")
            if isinstance(tile.occupant, Farm):
                farm = tile.occupant
                for i in range(farm.size[1]):
                    for j in range(farm.size[0]):
                        farm_tile = map.get_tile(farm.position[0] + j, farm.position[1] + i)
                        if farm_tile.has_resource():
                            farm_tile.resource.quantity -= amount
                            if farm_tile.resource.quantity <= 0:
                                farm_tile.resource = None
                if all(map.get_tile(farm.position[0] + j, farm.position[1] + i).resource is None for i in range(farm.size[1]) for j in range(farm.size[0])):
                    map.remove_building(farm)
            else:
                tile.resource.quantity -= amount
                if tile.resource.quantity <= 0:
                    tile.resource = None
        else:
            raise ValueError("Villager is not adjacent to a resource tile or resource tile is empty")

    def drop_resource(self, map):
        if self._is_adjacent_to_drop_point(map):
            collected = self.resource_collected
            self.resource_collected = 0
            print(f"{self} dropped {collected}")
            return collected
        else:
            raise ValueError("Villager is not adjacent to a TownCentre or Camp")

    def _is_adjacent(self, tile: Tile):
        return abs(self.position[0] - tile.position[0]) <= 1 and abs(self.position[1] - tile.position[1]) <= 1

    def _is_adjacent_to_drop_point(self, map):
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                x, y = self.position[0] + dx, self.position[1] + dy
                if 0 <= x < map.width and 0 <= y < map.height:
                    tile = map.get_tile(x, y)
                    if isinstance(tile.occupant, (TownCenter, Camp)):
                        return True
        return False

    def find_nearest_resource(self, map, resource_type=None):
        min_distance = float('inf')
        nearest_resource = None
        for y in range(map.height):
            for x in range(map.width):
                tile = map.get_tile(x, y)
                if tile.has_resource() and (resource_type is None or tile.resource.type == resource_type):
                    distance = math.sqrt((self.position[0] - x) ** 2 + (self.position[1] - y) ** 2)
                    if distance < min_distance:
                        min_distance = distance
                        nearest_resource = tile
        return nearest_resource

    def __repr__(self):
        return (f"Villager(name={self.name}, hp={self.hp}, attack={self.attack}, "
                f"speed={self.speed}, position={self.position}, carry_capacity={self.carry_capacity}, "
                f"resource_collected={self.resource_collected}, collection_rate={self.collection_rate})")