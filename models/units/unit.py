import pygame
from asyncio import PriorityQueue
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
        self.pos = (x, y)
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
        self.walkable_symbols = {Type.Food, Type.Farm, None, "Farm", "Food"} 
        self.health = hp  # Points de vie
        self.max_health = hp 
        self.status = unitStatus.IDLE
        self.grid.get_tile(x,y).unit.append(self)
        self.target = None
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
                self.move_toward(self.destination, self.grid)
                if not self.current_path:  # Arrivé à destination
                    self.status = unitStatus.IDLE
                    self.destination = None
        elif self.status == unitStatus.ATTACKING:
            if self.target and self.target.health > 0:
                if self.distance_to(self.target) <= self.attack_range:
                    self.atk(self.target)
                else:
                    self.status = unitStatus.MOVING
                    self.destination = self.target.pos
            else:
                self.status = unitStatus.IDLE
                self.target = None
        elif self.status == unitStatus.BUILDING:
            if self.distance_to(self.destination) > 1:
                self.move_toward(self.destination, self.grid)

    def distance_to(self, target):
        """Calculates distance to target unit"""
        x = abs(self.position[0] - target[0]) + abs(self.position[1] - target[1])
        return x
    
    def heuristic(self, a, b):
        """Fonction heuristique pour A* (distance de Chebyshev)."""
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def get_position(self):
        """Retourne la position actuelle de l'unité en coordonnées de tuiles."""
        return self.position

    def is_obstacle_on_path(self, current_path, grid):
        """Check if there are obstacles on the current path."""
        for pos in current_path:
            if grid.is_position_occupied(pos[0], pos[1]):
                return True
            return False
    
    def find_path(self, goal, current_path, grid, search_range=10):
        global last_calculated
        current_time = pygame.time.get_ticks() / 1000.0

        if (current_time - last_calculated < path_update_interval) and not self.is_obstacle_on_path(current_path, grid):
            #print("Pathfinding skipped due to time interval and no obstacle detected.")
            return current_path
        
        
        start = self.position
        print(f"Finding path from {start} to {goal}")

        open_set = []
        open_set.append((0, start))

        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}
        visited = set()

        def get_neighbors(pos):
          
            # Combinaisons de mouvements (cardinaux et diagonaux)
            moves = [
                (0, 1), (1, 0), (0, -1), (-1, 0),  # Mouvements cardinaux
                (1, 1), (1, -1), (-1, 1), (-1, -1)  # Mouvements diagonaux
            ]

            neighbors = []
            for dx, dy in moves:
                new_pos = (pos[0] + dx, pos[1] + dy)
                if (0 <= new_pos[0] < grid.largeur and 
                    0 <= new_pos[1] < grid.hauteur and
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

    def get_tile_cost(pos):
            base_cost = 1
            
            # Check for buildings directly from grid
            tile = grid.get_tile(pos[0], pos[1])
            if tile and hasattr(tile, 'occupant'):
                if tile.occupant and tile.occupant.unit_type == 'Building':
                    base_cost += 5  # High cost for buildings
            
            # Check for resources
            if tile and hasattr(tile, 'resource_type') and tile.resource_type:
                base_cost += 3  # Cost penalty for resources
                
            return base_cost

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
            
                for neighbor in get_neighbors(current):
                    if neighbor not in visited:
                        tile_cost = get_tile_cost(neighbor)
                        tentative_g_score = g_score[current] + tile_cost
                    
                        if (neighbor not in g_score or 
                            tentative_g_score < g_score[neighbor]):
                            came_from[neighbor] = current
                            g_score[neighbor] = tentative_g_score
                            f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, goal)
                            open_set.append((f_score[neighbor], neighbor))

            print(f"No path found - explored positions: {visited}")
            return []
    
    def move_toward(self, goal, grid, search_range=100):
        
        """Move unit towards goal using pathfinding and speed control."""
        if self.health <= 0:
            return False
        if self.position == goal:
            return False
        #self.status = unitStatus.MOVING
        
        # Calculer le temps écoulé depuis le dernier update
        current_time = pygame.time.get_ticks() / 1000.0  # Convertir en secondes
        elapsed_time = current_time - self.last_move_time
        
        # Accumuler la progression du mouvement basée sur la vitesse
        self.movement_accumulator = elapsed_time * self.speed  # self.speed est en tuiles/seconde
        
        # Si on n'a pas accumulé assez de mouvement pour avancer d'une tuile
        if self.movement_accumulator < 1.0:
            return False

        # Trouver un nouveau chemin si nécessaire
        if not self.current_path or self.is_obstacle_on_path(self.current_path, grid) :
            self.current_path = self.find_path(goal, self.current_path, grid, search_range)
            self.visited_path = [self.position]

        # S'il y a un chemin à suivre
        if self.current_path:
            # Tant qu'on a assez de mouvement accumulé et qu'il reste du chemin
            while self.movement_accumulator >= 1.0 and self.current_path and not self.is_obstacle_on_path(self.current_path, grid) :
                next_step = self.current_path[0]
                old_position = self.position
                
                try:
                    # Mettre à jour la position
                    self.position = next_step
                    self.pos = next_step
                    self.visited_path.append(next_step)
                    self.current_path.pop(0)
                    self.grid.update_unit_position(self, old_position, next_step)
                    #print(f"{self} move to {self.position}")
                    # Réduire l'accumulateur d'une unité pour chaque tuile parcourue
                    self.movement_accumulator -= 1.0
                    
                except Exception as e:
                    print(f"Error moving unit: {e}")
                    self.position = old_position
                    self.pos = old_position
                    return False

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
        if current_time - self.last_attack_time < 2.0:  # Enforce 1 second cooldown
            return
        """Simule une attaque contre une autre unité."""
        self.status == unitStatus.ATTACKING
        if self.health <= 0:
            return
        print(f"{self.unit_type} Attacked {target_unit} at {target_unit.position}, new health: {target_unit.health - self.atk_power}")
        target_unit.take_damage(self.atk_power)
        self.last_attack_time = current_time

    def take_damage(self, damage):
        """Réduit les points de vie de l'unité après une attaque."""
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.die()

    def die(self):
        """Gère la mort de l'unité."""
        print(f"L'unité {self.unit_type} est morte.")
        #self.grid.get_tile(self.position[0], self.position[1]).remove_unit(self)
        
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

