import pygame
from asyncio import PriorityQueue
from models.Resources.Terrain_type import Terrain_type  # Adjust the import path as necessary
from enum import Enum

class unitStatus(Enum):
    IDLE = "idle"
    GATHERING = "gathering"
    BUILDING = "building"
    MOVING = "moving"
    RETURNING_RESOURCES = "returning_resources"
    ATTACKING = "attacking"

class Unit:
    def __init__(self, x, y, unit_type, atk, speed, hp, map):
        self.position = (x, y)  # Position en termes de tuiles
        self.unit_type = unit_type  # Type d'unité (guerrier, archer)
        self.symbol = unit_type[0]
        self.atk_power = atk
        self.speed = speed  # Movement speed (tiles per second)
        self.move_cooldown = 0.9  # Time between moves in seconds
        self.last_move_time = 0  # Last time the unit moved
        self.remaining_move = 0
        self.destination = None
        self.path = []  # Liste du chemin
        self.grid = map  # Carte sur laquelle l'unité se déplace
        self.walkable_symbols = {Terrain_type.GRASS} 
        self.health = hp  # Points de vie
        self.max_health = hp 
        self.status = unitStatus.IDLE
    def update(self):
        """Met à jour l'unité, par exemple pour la faire se déplacer."""
        if self.destination:
            self.move_towards(self.destination)

    def heuristic(self, a, b):
        """Fonction heuristique pour A* (distance de Manhattan)."""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def get_position(self):
        """Retourne la position actuelle de l'unité en coordonnées de tuiles."""
        return self.position

    def find_path(self, goal, grid, search_range=10):
        start = self.position
        print(f"Finding path from {start} to {goal}")
        print(f"Manhattan distance: {self.heuristic(start, goal)}")

        open_set = []
        open_set.append((0, start))
        
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}
        visited = set()

        while open_set:
            current = min(open_set, key=lambda x: x[0])[1]
            open_set = [x for x in open_set if x[1] != current]
            
            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path

            visited.add(current)
            
            # Add diagonal movements
            neighbors = [
                (0, 1), (1, 0), (0, -1), (-1, 0),  # Cardinal directions
                (1, 1), (1, -1), (-1, 1), (-1, -1)  # Diagonal directions
            ]
            
            for direction in neighbors:
                neighbor = (current[0] + direction[0], current[1] + direction[1])
                
                if (0 <= neighbor[0] < len(grid) and 
                    0 <= neighbor[1] < len(grid[0])):
                    
                    if search_range is not None:
                        manhattan_dist = abs(neighbor[0] - start[0]) + abs(neighbor[1] - start[1])
                        if manhattan_dist > search_range:
                            continue

                    tile_type = grid[neighbor[0]][neighbor[1]].get_type()

                    if tile_type in self.walkable_symbols:
                        # Adjust movement cost for diagonal movement
                        move_cost = 1.4 if direction[0] != 0 and direction[1] != 0 else 1
                        tentative_g_score = g_score[current] + move_cost

                        if (neighbor not in g_score or 
                            tentative_g_score < g_score[neighbor]):
                            came_from[neighbor] = current
                            g_score[neighbor] = tentative_g_score
                            f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, goal)
                            if neighbor not in visited:
                                open_set.append((f_score[neighbor], neighbor))

        print(f"No path found - explored positions: {visited}")
        return []

    def move_towards(self, goal, map, search_range=10):
        """Move unit towards goal using pathfinding with speed control."""
        if self.health <= 0:
            return False

        current_time = pygame.time.get_ticks() / 1000.0  # Convert to seconds
        if current_time - self.last_move_time < self.move_cooldown / self.speed:
            return False  # Too soon to move again

        path = self.find_path(goal, map.get_grid(), search_range)
        
        if path:
            next_step = path[0]
            old_position = self.position
            try:
                self.position = next_step
                map.get_tile(old_position[0], old_position[1]).occupant = None
                map.get_tile(next_step[0], next_step[1]).occupant = self
                self.last_move_time = current_time
                print(f"{self.unit_type} moved to {next_step}")
                return True
            except Exception as e:
                print(f"Error moving unit: {e}")
                self.position = old_position
                return False
        
        return False

    def atk(self, target_unit):
        """Simule une attaque contre une autre unité."""
        self.status == unitStatus.ATTACKING
        if self.health <= 0:
            return
        print(f"{self.unit_type} Attacked {target_unit.unit_type} at {target_unit.position}, new health: {target_unit.health - self.atk_power}")
        target_unit.take_damage(self.atk_power)

    def take_damage(self, damage):
        """Réduit les points de vie de l'unité après une attaque."""
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.die()

    def die(self):
        """Gère la mort de l'unité."""
        print(f"L'unité {self.unit_type} est morte.")
        self.grid.get_tile(self.position[0], self.position[1]).remove_unit(self)

    def serialize(self):
        """Convertit une unité en un dictionnaire sérialisable."""
        return {
            "x": self.position[0],
            "y": self.position[1],
            "unit_type": self.unit_type,
            "atk": self.atk_power,
            "speed": self.speed,
            "hp": self.health
        }

    
    @classmethod
    def deserialize(cls, data, map):
        """Reconstruit une unité à partir d'un dictionnaire sérialisé."""
        return cls(
            x=data["x"],
            y=data["y"],
            unit_type=data["unit_type"],
            atk=data["atk"],
            speed=data["speed"],
            hp=data["hp"],
            map=map  # Passez la carte à l'unité
        )

