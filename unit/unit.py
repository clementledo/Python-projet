from map import Map
import time
from queue import PriorityQueue
from resource.tile import Type


class Unit:
    def __init__(self, x, y, unit_type, atk, speed, hp, map):
        #self.x = x  # Position X de l'unité
        #self.y = y  # Position Y de l'unité
        self.position = (x, y)
        self.unit_type = unit_type  # Type d'unité (guerrier, archer)
        self.symbol = unit_type[0]
        self.atk_power = atk
        self.speed = speed
        self.remaining_move = 0
        self.destination = None
        self.path = [] #
        self.grid = map
        self.walkable_symbols = {'Food', 'P', None, Type.Farm}
        self.health = hp  # Points de vie
        #map.update_unit_position(self, None, self.position)
    

    def heuristic(self, a, b):
        """Heuristic function for A* (Manhattan distance)."""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    def find_path(self, goal, map, search_range=10):
        """
        A* Pathfinding algorithm to find the shortest path from the unit's current position to a goal.

        :param goal: Tuple (x, y) goal position.
        :param search_range: Optional integer specifying the range to limit the search (a box around the start position).
        :return: List of tuples representing the path from start to goal, or empty list if no path found.
        """
        start = self.position

        # Check if the goal is walkable, if not, find the closest walkable tile
        if map[goal[1]][goal[0]].get_type() not in self.walkable_symbols:
            goal = self.find_closest_walkable(goal, map)

        # Priority queue for open nodes (unvisited positions)
        open_set = PriorityQueue()
        open_set.put((0, start))
        
        # Dictionary to keep track of the path (came from which node)
        came_from = {}
        
        # g_score: The cost of getting to each position
        g_score = {start: 0}
        
        # f_score: Estimated cost from start to goal (g + heuristic)
        f_score = {start: self.heuristic(start, goal)}
        
        # Visited set
        visited = set()
        
        while not open_set.empty():
            current = open_set.get()[1]

            # If goal is reached, reconstruct the path
            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                self.path = path  # Save the path in the unit's attribute
                return path

            visited.add(current)

            # Explore neighbors
            neighbors = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # 4 possible directions: down, right, up, left
            for direction in neighbors:
                neighbor = (current[0] + direction[0], current[1] + direction[1])

                # Check if the neighbor is within bounds
                if 0 <= neighbor[0] < len(map) and 0 <= neighbor[1] < len(map[0]):
                    
                    # Check if the tile is within the search range (if specified)
                    if search_range is not None:
                        if abs(neighbor[0] - start[0]) > search_range or abs(neighbor[1] - start[1]) > search_range:
                            continue
                    
                    # Check if the tile is walkable
                    if map[neighbor[1]][neighbor[0]].get_type() in self.walkable_symbols:
                        # Calculate tentative g_score
                        tentative_g_score = g_score[current] + 1  # Distance between adjacent nodes is 1

                        if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                            came_from[neighbor] = current
                            g_score[neighbor] = tentative_g_score
                            f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, goal)
                            
                            if neighbor not in visited:
                                open_set.put((f_score[neighbor], neighbor))

        # Return an empty list if no path is found
        return []    

    def find_closest_walkable(self, goal, map):
        """
        Find the closest walkable tile to the given goal.

        :param goal: Tuple (x, y) goal position.
        :param map: 2D list representing the map.
        :return: Tuple (x, y) closest walkable tile.
        """
        from collections import deque

        queue = deque([goal])
        visited = set()
        visited.add(goal)

        while queue:
            current = queue.popleft()
            if map[current[1]][current[0]].get_type() in self.walkable_symbols:
                return current

            neighbors = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            for direction in neighbors:
                neighbor = (current[0] + direction[0], current[1] + direction[1])
                if 0 <= neighbor[0] < len(map) and 0 <= neighbor[1] < len(map[0]) and neighbor not in visited:
                    queue.append(neighbor)
                    visited.add(neighbor)

        return goal  # If no walkable tile is found, return the original goal

    def move_towards(self, goal, map, search_range=10):
        """
        Move the unit towards a goal position using pathfinding. 
        The path is recalculated every time this method is called.

        :param goal: Tuple (x, y) goal position.
        :param search_range: Optional integer specifying the range to limit the search.
        """
        if self.health <= 0:
            return
        
        path = self.find_path(goal, map.grid, search_range)
        
        if path:
            # Move to the next step in the path
            next_step = path[0]
            old_position = self.position
            # Calculate the amount of movement this turn based on speed
            self.remaining_move += self.speed
            #Only move to the next tile if the unit has enough speed to cover one tile
            if self.remaining_move >= 1.0:
                # Move to the next tile
                self.position = next_step
                self.remaining_move -= 1.0  # Reduce the remaining movement by 1 tile
                #self.print_grid_with_unit()
            
            if old_position != self.position:
                print(f"{self.unit_type} Moved to {next_step}")
                map.update_unit_position(self, old_position, self.position)
            else:
                print(f"{self.unit_type} is moving to {next_step}")
        else:
            print("No path found or out of range.")

    def print_grid_with_unit(self):
        """
        Print the grid with the unit's current position marked as 'U'.
        """
        # Make a copy of the grid to temporarily modify it
        temp_grid = [row.copy() for row in self.grid]
        
        # Mark the unit's position with 'U'
        unit_x, unit_y = self.position
        temp_grid[unit_x][unit_y] = 'U'
        
        # Print the grid
        for row in temp_grid:
            print(' '.join(row))
        print()  # Add an extra newline for better readability
    
    def atk(self, target_unit):
        #Simulate an attack on another unit, reducing its health.
        if self.health <= 0:
            return
        print(f"{self.unit_type} Attacked unit {target_unit.unit_type} at {target_unit.position}, new health: {target_unit.health - self.atk_power}")
        target_unit.take_damage(self.atk_power)

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.die()

    def die(self):
        print(f"L'unité {self.unit_type} est morte.")
        self.grid.get_tile(self.position[0], self.position[1]).remove_unit(self)