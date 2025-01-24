import pygame
from queue import PriorityQueue
from models.Resources.Terrain_type import Terrain_type  # Adjust the import path as necessary
from enum import Enum
from models.Buildings.building import Building
from models.Resources.Tile import Type

last_calculated = 0
path_update_interval = 5

class unitStatus(Enum):
    IDLE = "idle"
    GATHERING = "gathering"
    BUILDING = "building"
    MOVING = "moving"
    RETURNING_RESOURCES = "returning_resources"
    ATTACKING = "attacking"

class Unit:
    def __init__(self, x, y, unit_type, speed, attack_speed, hp, map):
        self.x = x
        self.y = y
        self.position = (x, y)
        self.unit_type = unit_type
        self.speed = speed
        self.attack_speed = attack_speed
        self.attack_range = 1  # Default melee range
        self.atk_power = 5  # Default attack power
        self.health = hp
        self.max_health = hp
        self.status = unitStatus.IDLE
        self.symbol = unit_type[0]
        self.move_cooldown = 0.9  # Time between moves in seconds
        self.last_move_time = 0  # Last time the unit moved
        self.remaining_move = 0
        self.destination = None
        self.path = []  # Liste du chemin
        self.grid = map  # Carte sur laquelle l'unité se déplace
        self.walkable_symbols = {Type.Food, Type.Farm, None, "Farm", "Food", "Unit"} 
        self.health = hp  # Points de vie
        self.max_health = hp 
        self.status = unitStatus.IDLE
        #map.update_unit_position(self, None, (x, y))

        self.current_path = []  # Store current path for visualization
        self.show_path = True   # Toggle path visibility
        self.visited_path = []  # Store visited path points
        self.path_segment_length = 3  # Number of future points to show
        self.movement_accumulator = 0.0  # Stocke la progression du déplacement 
        self.last_move_time = pygame.time.get_ticks() / 1000.0
        self.last_attack_time = 0.0

    def update(self):
        """Update unit state"""
        if self.status == unitStatus.MOVING:
            if self.destination:
                # Appeler move_towards pour effectuer le déplacement progressif
                self.move_towards(self.destination, self.grid)
                if not self.current_path:  # Arrivé à destination
                    self.status = unitStatus.IDLE
                    self.destination = None
        elif self.status == unitStatus.ATTACKING:
            if self.target and self.target.health > 0:
                if self.distance_to(self.target.position) <= self.attack_range:
                    self.atk(self.target)
                else:
                    self.status = unitStatus.MOVING
                    self.destination = self.target.position
            else:
                self.status = unitStatus.IDLE
                self.target = None
        elif self.status == unitStatus.BUILDING:
            if self.distance_to(self.destination) > 1:
                self.move_towards(self.destination, self.grid)
    
    def distance_to(self, target):
        """Calculate distance to target position"""
        return abs(self.position[0] - target[0]) + abs(self.position[1] - target[1])
    def heuristic(self, a, b):
        """Fonction heuristique pour A* (distance de Chebyshev)."""
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def get_position(self):
        """Retourne la position actuelle de l'unité en coordonnées de tuiles."""
        return self.position

    
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
            if map[current[1]][current[0]].occupant in self.walkable_symbols:
                return current

            neighbors = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            for direction in neighbors:
                neighbor = (current[0] + direction[0], current[1] + direction[1])
                if 0 <= neighbor[0] < len(map) and 0 <= neighbor[1] < len(map[0]) and neighbor not in visited:
                    queue.append(neighbor)
                    visited.add(neighbor)

        return goal  # If no walkable tile is found, return the original goal
    
    def is_obstacle_on_path(self, current_path, grid):
        """Check if there are obstacles on the current path."""
        for pos in current_path:
            if grid.is_position_occupied(pos[0], pos[1]):
                return True
            return False
    
    def find_path(self, goal, current_path, grid):
        global last_calculated
        current_time = pygame.time.get_ticks() / 1000.0

        if (current_time - last_calculated < path_update_interval) and not self.is_obstacle_on_path(current_path, grid):
            print("Pathfinding skipped due to time interval and no obstacle detected.")
            return current_path
        
        """A* pathfinding avec prise en charge des mouvements diagonaux."""
        start = self.position
        if start == goal:
            return []
        print(f"Finding path from {start} to {goal}")

        open_set = []
        open_set.append((0, start))

        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}
        visited = set()

        def get_neighbors(pos):
            """Récupère les voisins valides en évitant les obstacles (unités, mines, et bâtiments)."""
            # Combinaisons de mouvements (cardinaux et diagonaux)
            moves = [
                (0, 1), (1, 0), (0, -1), (-1, 0),  # Mouvements cardinaux
                (1, 1), (1, -1), (-1, 1), (-1, -1)  # Mouvements diagonaux
            ]

            neighbors = []
            for dx, dy in moves:
                new_pos = (pos[0] + dx, pos[1] + dy)
                if (grid.is_walkable(new_pos[0], new_pos[1]) and
                    not grid.is_position_occupied(new_pos[0], new_pos[1])):
                    neighbors.append(new_pos)

            return neighbors

        while open_set:
            open_set.sort(key=lambda x: x[0])
            _, current = open_set.pop(0)

            if current in visited:
                continue

            visited.add(current)

            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                last_calculated = current_time
                return path

            for neighbor in get_neighbors(current):
                tentative_g_score = g_score[current] + 1

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, goal)

                    open_set.append((f_score[neighbor], neighbor))

        return None  # Aucun chemin trouvé

    def move_towards(self, goal, grid):
        """Move unit towards goal using pathfinding and smooth movement."""
        if self.health <= 0:
            return False

        self.status = unitStatus.MOVING

        # Calculer le temps écoulé depuis le dernier update
        current_time = pygame.time.get_ticks() / 1000.0  # Convertir en secondes
        elapsed_time = current_time - self.last_move_time

        if elapsed_time <= 0:
            return False

        # Trouver un nouveau chemin si nécessaire
        if not self.current_path or self.is_obstacle_on_path(self.current_path, grid):
            self.current_path = self.find_path(goal, self.current_path, grid)
            self.visited_path = [self.position]
            self.path_progress = 0  # Initialiser la progression dans la première tuile

        # S'il y a un chemin à suivre
        if self.current_path:
            # Obtenir la prochaine étape dans le chemin
            next_step = self.current_path[0]
            start_x, start_y = self.position
            target_x, target_y = next_step

            # Calculer le déplacement nécessaire entre les deux positions
            dx = target_x - start_x
            dy = target_y - start_y
            distance_to_target = (dx**2 + dy**2) ** 0.5

            # Calculer la distance que l'unité peut parcourir pendant le temps écoulé
            distance_to_move = self.speed * elapsed_time

            # Si l'unité peut atteindre ou dépasser la prochaine tuile
            if distance_to_move >= distance_to_target:
                # Déplacer complètement vers la prochaine tuile
                self.position = next_step
                self.visited_path.append(next_step)
                self.current_path.pop(0)
                self.last_move_time = current_time

                # Réinitialiser la progression
                self.path_progress = 0

            else:
                # Mouvement partiel vers la prochaine tuile
                self.path_progress += distance_to_move / distance_to_target

                # Calculer la nouvelle position interpolée
                self.position = (
                    start_x + dx * self.path_progress,
                    start_y + dy * self.path_progress
                )

                self.last_move_time = current_time

            return True

        return False


    def get_path_for_rendering(self):
        """Return current visible path segment"""
        if self.show_path and self.current_path:
            # Return current position and next few points
            return [self.position] + self.current_path[:self.path_segment_length]
        return []

    def atk(self, target_unit):
        current_time = pygame.time.get_ticks() / 1000.0
        if current_time - self.last_attack_time < 1.0:  # Enforce 1 second cooldown
            return
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
        self.grid.get_tile(self.position[0], self.position[1]).occupant = None

    def serialize(self):
        """Serialize unit data"""
        return {
            "x": self.x,
            "y": self.y,
            "position": self.position,
            "unit_type": self.unit_type,
            "speed": self.speed,
            "attack_speed": self.attack_speed,
            "attack_range": self.attack_range,
            "atk_power": self.atk_power,
            "health": self.health,
            "max_health": self.max_health,
            "status": self.status.value,
            "player_id": self.player_id if hasattr(self, 'player_id') else None
        }

    @classmethod
    def deserialize(cls, data, map):
        """Deserialize unit data"""
        unit = cls(data["x"], data["y"], data["unit_type"], 
                  data["speed"], data["attack_speed"], data["health"], map)
        unit.position = data["position"]
        unit.attack_range = data["attack_range"]
        unit.atk_power = data["atk_power"]
        unit.max_health = data["max_health"]
        unit.status = unitStatus(data["status"])
        if "player_id" in data:
            unit.player_id = data["player_id"]
        return unit
