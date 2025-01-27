import random
from models.Resources.Tile import Tile
from models.Resources.Ressource import Resource
from models.Resources.Terrain_type import Terrain_type
import numpy as np

class Map:
    def __init__(self, largeur, hauteur, type_carte="ressources_generales"):
        self.largeur = largeur
        self.hauteur = hauteur
        self.grille = [[Tile(x, y) for x in range(largeur)] for y in range(hauteur)]
        # Cache for occupied positions
        self._occupied_positions = set()
        # Cache for building positions with their sizes
        self._building_areas = {}
        # Cache for unit positions
        self._unit_positions = set()
        self.generer_aleatoire(type_carte)

    def update_caches(self, game_state):
        """Update position caches"""
        self._occupied_positions.clear()
        self._unit_positions.clear()
        self._building_areas.clear()

        # Cache unit positions
        for unit in game_state.model['units']:
            self._unit_positions.add((unit.x, unit.y))
            self._occupied_positions.add((unit.x, unit.y))

        # Cache building areas
        for building in game_state.model['buildings']:
            bx, by = building.pos
            width, height = building.size
            self._building_areas[(bx, by)] = (width, height)
            # Add all building tiles to occupied positions
            for x in range(bx, bx + width):
                for y in range(by, by + height):
                    self._occupied_positions.add((x, y))

    def get_grid(self):
        return self.grille
    
    def get_tile(self, x, y):
        """Optimized tile getter with bounds check"""
        if 0 <= x < self.largeur and 0 <= y < self.hauteur:
            return self.grille[y][x]
        return None

    def is_position_occupied(self, x, y, game_state=None):
        """Optimized position check using caches"""
        if not game_state:
            return False

        # Update caches if needed (could be done less frequently)
        if not self._occupied_positions:
            self.update_caches(game_state)

        return (x, y) in self._occupied_positions

    def is_walkable(self, x, y):
        """Fast walkable check"""
        if not (0 <= x < self.largeur and 0 <= y < self.hauteur):
            return False
        return self.grille[y][x].terrain_type != Terrain_type.WATER

   

    def generer_aleatoire(self, type_carte="centre_ressources"):
        """
        Génère une carte aléatoire selon le type de carte sélectionné.
        Par défaut, toutes les tuiles sont initialisées sans ressources.

        Args:
            type_carte (str): Type de génération ("ressources_generales", "centre_ressources", "low_ressources").
        """
        # Initialiser la grille avec des tuiles sans ressources
        self.grille = [[Tile(x, y) for x in range(self.largeur)] for y in range(self.hauteur)]

        largeur, hauteur = self.largeur, self.hauteur
        total_cases = largeur * hauteur

        if type_carte in ["ressources_generales", "low_ressources"]:
            pourcent = 50 if type_carte == "ressources_generales" else 65
            total_ressources = total_cases // pourcent

            # Générer des positions aléatoires uniques
            positions = np.random.choice(total_cases, total_ressources, replace=False)
            x_coords, y_coords = positions % largeur, positions // largeur

            # Générer les ressources de manière vectorisée
            resource_types = np.random.choice(["Wood", "Gold"], size=total_ressources)
            for x, y, r_type in zip(x_coords, y_coords, resource_types):
                self.grille[y][x].resource = Resource(
                    r_type, [100, 0, 0] if r_type == "Wood" else [0, 800, 0]
                )

        elif type_carte == "centre_ressources":
            # Définir le centre et le rayon
            centre_x, centre_y = largeur // 2, hauteur // 2
            radius_x, radius_y = largeur // 6, hauteur // 6

            # Créer une grille de coordonnées
            x_coords, y_coords = np.meshgrid(np.arange(largeur), np.arange(hauteur))
            x_coords, y_coords = x_coords.flatten(), y_coords.flatten()

            # Calculer le masque ovale
            mask_oval = ((x_coords - centre_x) ** 2) / (radius_x ** 2) + \
                        ((y_coords - centre_y) ** 2) / (radius_y ** 2) <= 1

            # Séparer les positions à l'intérieur et à l'extérieur de l'ovale
            inside_positions = np.where(mask_oval)[0]
            outside_positions = np.where(~mask_oval)[0]

            # Sélectionner les positions pour "Gold" (dans l'ovale) et "Wood" (en dehors)
            total_gold = min(len(inside_positions), total_cases // 25)
            total_wood = min(len(outside_positions), total_cases // 65)

            gold_indices = np.random.choice(inside_positions, total_gold, replace=False)
            wood_indices = np.random.choice(outside_positions, total_wood, replace=False)

            # Assigner les ressources "Gold"
            for idx in gold_indices:
                x, y = x_coords[idx], y_coords[idx]
                self.grille[y][x].resource = Resource("Gold", [0, 800, 0])

            # Assigner les ressources "Wood"
            for idx in wood_indices:
                x, y = x_coords[idx], y_coords[idx]
                self.grille[y][x].resource = Resource("Wood", [100, 0, 0])

        else:
            raise ValueError(f"Type de carte non reconnu : {type_carte}")
            


    def update_unit_position(self, unit, old_pos, new_pos):
        """Update unit position on the map."""
        # Remove unit from old tile
        if old_pos:
            old_tile = self.get_tile(old_pos[0], old_pos[1])
            if old_tile:
                old_tile.occupant = None
                old_tile.unit.remove(unit)
            
        # Add unit to new tile
        new_tile = self.get_tile(new_pos[0], new_pos[1])
        if new_tile:
            new_tile.occupant = "Unit"
            new_tile.unit.append(unit)
            return True
        return False

    def place_building(self, building):
        """
        Place a building on the map, marking all the tiles it occupies.
        Buildings may occupy multiple tiles (e.g., Town Hall is 4x4).
        """
        x, y = building.pos
        width, height = building.size
        x -= width // 2
        y -= height // 2
        
        # Check if the space is free and within bounds
        if not self.is_area_free(x, y, width, height):
            raise ValueError("Building can't be placed: space is either occupied or out of bounds.")

        # Mark the tiles as occupied by the building
        for i in range(width):
            for j in range(height):
                self.grille[y + j][x + i].occupant = building.name  # Mark the grid with the building reference
    
    def is_area_free(self, top_left_x, top_left_y, width, height):
        top_left_x += 1
        top_left_y += 1
        for i in range(width):
            for j in range(height):
                if not self.is_within_bounds(top_left_x - i, top_left_y - j) or self.is_tile_occupied(top_left_x - i, top_left_y - j):
                    return False
        return True
    
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
                if tile and tile.resource != None:
                    resources.append((x, y))
        return resources
    
    def set_resources(self):
        resource = self.get_resources()
        for r in resource:
            if self.grille[r[1]][r[0]].occupant == None:
                self.grille[r[1]][r[0]].occupant = self.grille[r[1]][r[0]].resource.resource_type

    def __repr__(self):
        return f"Map({self.largeur}x{self.hauteur})"
