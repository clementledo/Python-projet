class Unit:
    def __init__(self, x, y, unit_type, atk, speed, hp, map):
        self.position = (x, y)  # Position en termes de tuiles
        self.unit_type = unit_type  # Type d'unité (guerrier, archer)
        self.symbol = unit_type[0]
        self.atk_power = atk
        self.speed = speed
        self.remaining_move = 0
        self.destination = None
        self.path = []  # Liste du chemin
        self.grid = map  # Carte sur laquelle l'unité se déplace
        self.walkable_symbols = {'Food', 'P', None}
        self.health = hp  # Points de vie

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

    def find_path(self, goal, map, search_range=10):
        """
        Algorithme A* pour trouver le chemin le plus court de la position actuelle
        à un objectif donné.
        """
        start = self.position

        # Priority queue pour les noeuds à explorer
        open_set = PriorityQueue()
        open_set.put((0, start))

        # Dictionnaire pour suivre le chemin
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}
        visited = set()

        while not open_set.empty():
            current = open_set.get()[1]

            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                self.path = path  # Sauvegarde du chemin
                return path

            visited.add(current)

            neighbors = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # 4 directions possibles
            for direction in neighbors:
                neighbor = (current[0] + direction[0], current[1] + direction[1])

                if 0 <= neighbor[0] < len(map) and 0 <= neighbor[1] < len(map[0]):
                    if search_range is not None:
                        if abs(neighbor[0] - start[0]) > search_range or abs(neighbor[1] - start[1]) > search_range:
                            continue

                    if map[neighbor[0]][neighbor[1]].get_type() in self.walkable_symbols:
                        tentative_g_score = g_score[current] + 1

                        if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                            came_from[neighbor] = current
                            g_score[neighbor] = tentative_g_score
                            f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, goal)

                            if neighbor not in visited:
                                open_set.put((f_score[neighbor], neighbor))

        return []  # Aucun chemin trouvé

    def move_towards(self, goal, map, search_range=10):
        """
        Déplace l'unité vers un objectif en utilisant la fonction de pathfinding.
        """
        if self.health <= 0:
            return

        path = self.find_path(goal, map.grid, search_range)

        if path:
            next_step = path[0]
            old_position = self.position
            self.remaining_move += self.speed

            if self.remaining_move >= 1.0:
                self.position = next_step
                self.remaining_move -= 1.0

            if old_position != self.position:
                print(f"{self.unit_type} moved to {next_step}")
                map.update_unit_position(self, old_position, self.position)  # Mise à jour de la position sur la carte
            else:
                print(f"{self.unit_type} is moving to {next_step}")
        else:
            print("No path found or out of range.")

    def atk(self, target_unit):
        """Simule une attaque contre une autre unité."""
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
