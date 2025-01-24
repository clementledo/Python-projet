import random
from models.Resources.Tile import Tile
from models.Resources.Ressource import Resource
from models.Resources.Terrain_type import Terrain_type

class Map:
    def __init__(self, largeur, hauteur, type_carte="ressources_generales"):
        self.largeur = largeur
        self.hauteur = hauteur
        self.grille = [[Tile(x, y) for x in range(largeur)] for y in range(hauteur)]
        self.generer_aleatoire(type_carte)
    """l"""
    def get_grid(self):
        return self.grille
    
    def get_tile(self, x, y):
        """Get tile at specified coordinates."""
        if 0 <= x < self.largeur and 0 <= y < self.hauteur:
            return self.grille[y][x]
        return None

    

    def is_position_occupied(self, x, y, game_state=None):
        """Vérifie si une position est occupée par une unité ou un bâtiment"""
        if not game_state:
            return False
            
        # Vérification des unités
        for unit in game_state.model['units']:
            if unit.x == x and unit.y == y:
                return True
                
        # Vérification des bâtiments
        for building in game_state.model['buildings']:
            bx, by = building.pos
            width, height = building.size
            # Vérifie si la position est dans l'emprise du bâtiment
            if (x >= bx and x < bx + width and 
                y >= by and y < by + height):
                return True
                
        return False

    def is_walkable(self, x, y):
        """Vérifie si une position est accessible pour une unité"""
        # Check map boundaries
        if x < 0 or x >= self.largeur or y < 0 or y >= self.hauteur:
            return False
            
        # Check if tile exists and is walkable terrain
        try:
            tile = self.grille[y][x]
            return tile.terrain_type == Terrain_type.GRASS
        except IndexError:
            return False


    def generer_aleatoire(self, type_carte="centre_ressources"):
        """
        Génère une carte aléatoire selon le type de carte sélectionné.
        Par défaut, toutes les tuiles sont initialisées sans ressources.
        
        Args:
            type_carte (str): Type de génération ("ressources_generales","centre_ressources","low_ressources").
        """
        # Initialiser la grille avec des tuiles sans ressources
        for y in range(self.hauteur):
            for x in range(self.largeur):
                self.grille[y][x] = Tile(x, y)  # Chaque tuile est vide par défaut

        if type_carte in ["ressources_generales","low_ressources"]:
            
            pourcent = 50 if type_carte == "ressources_generales" else 65
            
            # Répartition aléatoire des ressources sur toute la carte
            for _ in range((self.largeur * self.hauteur) // pourcent):  # Environ 10% des cases ont des ressources
                x = random.randint(0, self.largeur - 1)
                y = random.randint(0, self.hauteur - 1)
                if not self.is_position_occupied(x,y):

                    resource_type = random.choice(["Wood", "Gold"])
                    if resource_type == "Wood":
                        self.grille[y][x].resource = Resource(resource_type, [100, 0, 0]) 
                    else:
                        self.grille[y][x].resource = Resource(resource_type, [0, 800, 0]) 

        elif type_carte == "centre_ressources":
            # Concentration des ressources au centre de la carte
            centre_x = self.largeur // 2
            centre_y = self.hauteur // 2
            radius_x = self.largeur // 6  # Réduction du rayon horizontal
            radius_y = self.hauteur // 6  # Réduction du rayon vertical

            for _ in range((self.largeur * self.hauteur) // 25):  # Environ 10% des cases ont des ressources
                while True:
                    # Générer des positions dans une forme ovale

                    x = random.randint(0, self.largeur - 1)
                    y = random.randint(0, self.hauteur - 1)
                    if ((x - centre_x) ** 2) / (radius_x ** 2) + ((y - centre_y) ** 2) / (radius_y ** 2) <= 1:
                        break

                self.grille[y][x].resource = Resource("Gold", [0, 800, 0])  # Exemple de ressources

            # Ajouter des ressources "Wood" en dehors du cercle
            for _ in range((self.largeur * self.hauteur) // 65):  # Environ 10% des cases ont des ressources
                while True:
                    # Générer des positions en dehors de l'ovale
                    x = random.randint(0, self.largeur - 1)
                    y = random.randint(0, self.hauteur - 1)
                    if ((x - centre_x) ** 2) / (radius_x ** 2) + ((y - centre_y) ** 2) / (radius_y ** 2) > 1:
                        break

                self.grille[y][x].resource = Resource("Wood", [100, 0, 0])  # Exemple de ressources

        else:
            raise ValueError(f"Type de carte non reconnu : {type_carte}")

    def update_unit_position(self, unit, old_pos, new_pos):
        """Update unit position on the map."""
        # Remove unit from old tile
        old_tile = self.get_tile(old_pos[0], old_pos[1])
        if old_tile:
            old_tile.occupant = None
            
        # Add unit to new tile
        new_tile = self.get_tile(new_pos[0], new_pos[1])
        if new_tile:
            new_tile.occupant = unit
            return True
        return False

    def place_building(self, building):
        """
        Place a building on the map, marking all the tiles it occupies.
        Buildings may occupy multiple tiles (e.g., Town Hall is 4x4).
        """
        x, y = building.pos
        width, height = building.size

        # Check if the space is free and within bounds
        if not self.is_area_free(x, y, width, height):
            raise ValueError("Building can't be placed: space is either occupied or out of bounds.")

        # Mark the tiles as occupied by the building
        for i in range(width):
            for j in range(height):
                self.grille[y + j][x + i].occupant = building.name  # Mark the grid with the building reference
    
    def is_area_free(self, top_left_x, top_left_y, width, height):
        for i in range(width):
            for j in range(height):
                if not self.is_within_bounds(top_left_x + i, top_left_y + j) or self.is_tile_occupied(top_left_x + i, top_left_y + j):
                    return False
    
    def is_within_bounds(self, x, y):
        return 0 <= x < self.largeur and 0 <= y < self.hauteur

    def is_tile_occupied(self, x, y):
        return self.grille[y][x].occupant != None
    
    def serialize(self):
        """Sérialise la carte sous forme de dictionnaire."""
        return {
            "largeur": self.largeur,
            "hauteur": self.hauteur,
            "grille": [
                [
                    tile.serialize() if tile else None
                    for tile in ligne
                ]
                for ligne in self.grille
            ]
        }
    
    @classmethod
    def deserialize(cls, data):
        """Recrée une carte à partir des données sérialisées."""
        map_instance = cls(data["largeur"], data["hauteur"])
        map_instance.grille = [
            [
                Tile.deserialize(tile_data) if tile_data else None
                for tile_data in ligne
            ]
            for ligne in data["grille"]
        ]
        return map_instance

    def get_resources(self):
        """Retourne une liste de positions de ressources sur la carte"""
        resources = []
        for y in range(self.hauteur):
            for x in range(self.largeur):
                tile = self.get_tile(x, y)
                if tile and isinstance(tile, Resource):
                    resources.append((x, y))
        return resources

    def __repr__(self):
        return f"Map({self.largeur}x{self.hauteur})"
