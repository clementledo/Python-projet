from models.Resources.resource_type import ResourceType

class Unit:
    def __init__(self, name, hp, attack, speed, range=1, position=(0, 0), symbol=""):
        self.name = name
        self.hp = hp
        self.attack = attack
        self.speed = speed
        self.range = range
        self.position = position
        self.symbol = symbol

    def __repr__(self):
        return (f"Unit(name={self.name}, hp={self.hp}, attack={self.attack}, "
                f"speed={self.speed}, range={self.range}, position={self.position} symbol={self.symbol})")

    def move(self, map, target_position):
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
        goal = target_position
        frontier = PriorityQueue()
        frontier.put((0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}

        while not frontier.empty():
            _, current = frontier.get()

            if current == goal:
                break

            for next in neighbors(current):
                tile = map.get_tile(next[0], next[1])
                if tile.is_occupied() or (tile.has_resource() and tile.resource.type in [ResourceType.WOOD, ResourceType.GOLD]):
                    continue
                new_cost = cost_so_far[current] + heuristic(current, next)
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + heuristic(goal, next)
                    frontier.put((priority, next))
                    came_from[next] = current

        if goal not in came_from:
            raise ValueError("No valid path to target position")

        path = []
        current = goal
        while current != start:
            path.append(current)
            current = came_from[current]
        path.reverse()

        if path:
            self.position = path[-1]

    def move_to(self, map, target):
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
        goal = target.position
        frontier = PriorityQueue()
        frontier.put((0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}

        while not frontier.empty():
            _, current = frontier.get()

            if current == goal:
                break

            for next in neighbors(current):
                tile = map.get_tile(next[0], next[1])
                if tile.is_occupied() or (tile.has_resource() and tile.resource.type in [ResourceType.WOOD, ResourceType.GOLD]):
                    continue
                new_cost = cost_so_far[current] + heuristic(current, next)
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + heuristic(goal, next)
                    frontier.put((priority, next))
                    came_from[next] = current

        if goal not in came_from:
            # Find the closest adjacent tile
            closest_tile = None
            min_distance = float('inf')
            for next in neighbors(goal):
                if next in came_from:
                    distance = heuristic(next, goal)
                    if distance < min_distance:
                        min_distance = distance
                        closest_tile = next
            if closest_tile is None:
                return  # No valid path to target position or adjacent tiles
            goal = closest_tile

        path = []
        current = goal
        while current != start:
            path.append(current)
            current = came_from[current]
        path.reverse()

        if path:
            self.position = path[-1]

    def attack_unit(self, target):
        if self.hp <= 0 or target.hp <= 0:
            raise ValueError("One of the units is already dead")
        if abs(self.position[0] - target.position[0]) > 1 or abs(self.position[1] - target.position[1]) > 1:
            raise ValueError("Target is not adjacent")
        target.hp -= self.attack
        if target.hp < 0:
            target.hp = 0
