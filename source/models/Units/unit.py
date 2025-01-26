from models.Buildings.building import Building
from models.Units.status import Status

class Unit:
    def __init__(self, name, hp, attack, speed, range=1, position=(0, 0), symbol=""):
        self.name = name
        self.hp = hp
        self.attack = attack
        self.speed = speed
        self.range = range
        self.position = position
        self.symbol = symbol
        self.status = Status.INACTIVE  # Use Status enum
        self.path = []  # Path of the unit
        self.move_progress = 0 # Progress of the unit
        self.move_speed = 0.1 # Speed of move (in % per frame)

    def __repr__(self):
        return (f"Unit(name={self.name}, hp={self.hp}, attack={self.attack}, "
                f"speed={self.speed}, range={self.range}, position={self.position}, "
                f"symbol={self.symbol}, status={self.status})")

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

        def adjacent_positions(building_position, building_size):
            x, y = building_position
            width, height = building_size
            positions = []
            for dx in range(-1, width + 1):
                for dy in range(-1, height + 1):
                    if (dx == -1 or dx == width) or (dy == -1 or dy == height):
                        positions.append((x + dx, y + dy))
            return filter(lambda p: 0 <= p[0] < map.width and 0 <= p[1] < map.height, positions)

        start = self.position
        goal_positions = adjacent_positions(target_position, (4, 4))  # Assuming building size is 4x4
        goal_positions = list(goal_positions)

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

        if goal not in came_from:
            # Find the closest possible position
            closest_tile = None
            min_distance = float('inf')
            for next in neighbors(goal_positions[0]):
                if next in came_from:
                    distance = heuristic(next, goal_positions[0])
                    if distance < min_distance:
                        min_distance = distance
                        closest_tile = next
            if closest_tile is None:
                print(f"No valid path from {start} to {target_position}")
                self.status = Status.INACTIVE  # Update status to inactive
                return  # No valid path to target position
            goal = closest_tile

        path = []
        current = goal
        while current != start:
            path.append(current)
            current = came_from[current]
        path.reverse()
        self.path = path  # Store the path in the unit
        self.move_progress = 0 #Initialize progress
        self.status = Status.WALKING  # Update status to walking
        self.map = map #Store the map in the unit

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
                if tile.is_occupied() and not isinstance(tile.occupant, Unit) and not tile.occupant.walkable:
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

        self.path = path # Store the path in the unit
        self.move_progress = 0 #Initialize progress
        self.status = Status.WALKING  # Update status to walking
        self.map = map #Store the map in the unit

    def attack_target(self, target, map, player):
        if self.hp <= 0 or target.hp <= 0:
            raise ValueError("One of the units is already dead")
        if abs(self.position[0] - target.position[0]) > 1 or abs(self.position[1] - target.position[1]) > 1:
            raise ValueError("Target is not adjacent")
        target.hp -= self.attack
        if target.hp <= 0:
            target.hp = 0
            if isinstance(target, Unit):
                map.remove_unit(target)
                player.remove_unit(target)
            elif isinstance(target, Building):
                map.remove_building(target)
                player.remove_building(target)
        self.status = Status.ATTACKING  # Update status to attacking

    def update_position(self):
        """Update the position of the unit along its path."""
        if self.status == Status.WALKING and self.path:
            if self.move_progress < 1:
                self.move_progress = min(1, self.move_progress + self.move_speed)
            else :
              self.map.remove_unit(self)
              self.position = self.path.pop(0) # Move to the next position
              self.map.add_unit(self)
              self.move_progress = 0
              if not self.path:
                 self.status = Status.INACTIVE