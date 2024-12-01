import random
from models.Resources.Tile import Tile
from models.Resources.Ressource import Resource
from models.Resources.Terrain_type import Terrain_type

class Map:
    def __init__(self, largeur, hauteur, type_carte="ressources_generales"):
        self.largeur = largeur
        self.hauteur = hauteur
        self.grille = [[None for _ in range(largeur)] for _ in range(hauteur)]
        self.generer_aleatoire(type_carte)
    

    def generer_aleatoire2(self, type_carte="ressources_generales"):
        """Génère une carte où toutes les tuiles sont de type GRASS."""
        for y in range(self.hauteur):
            for x in range(self.largeur):
                self.grille[y][x] = Tile(x, y)

    def generer_aleatoire(self, type_carte="ressources_generales"):
        """
        Génère une carte aléatoire selon le type de carte sélectionné.
        Par défaut, toutes les tuiles sont initialisées sans ressources.
        
        Args:
            type_carte (str): Type de génération ("ressources_generales" ou "centre_ressources").
        """
        # Initialiser la grille avec des tuiles sans ressources
        for y in range(self.hauteur):
            for x in range(self.largeur):
                self.grille[y][x] = Tile(x, y)  # Chaque tuile est vide par défaut

        if type_carte == "ressources_generales":
            # Répartition aléatoire des ressources sur toute la carte
            for _ in range((self.largeur * self.hauteur) // 10):  # Environ 10% des cases ont des ressources
                x = random.randint(0, self.largeur - 1)
                y = random.randint(0, self.hauteur - 1)
                resource_type = random.choice(["Wood", "Gold", "Food"])
                self.grille[y][x].resource = Resource(resource_type, [100, 100, 100])  # Exemple de ressources

        elif type_carte == "centre_ressources":
            # Concentration des ressources au centre de la carte
            centre_x = self.largeur // 2
            centre_y = self.hauteur // 2
            radius = min(self.largeur, self.hauteur) // 4  # Rayon pour concentrer les ressources

            for _ in range((self.largeur * self.hauteur) // 10):  # Environ 10% des cases ont des ressources
                # Générer des positions autour du centre
                x = random.randint(max(0, centre_x - radius), min(self.largeur - 1, centre_x + radius))
                y = random.randint(max(0, centre_y - radius), min(self.hauteur - 1, centre_y + radius))
                resource_type = random.choice(["Wood", "Gold", "Food"])
                self.grille[y][x].resource = Resource(resource_type, [100, 100, 100])  # Exemple de ressources

        else:
            raise ValueError(f"Type de carte non reconnu : {type_carte}")



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

    def __repr__(self):
        return f"Map({self.largeur}x{self.hauteur})"
