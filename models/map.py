import random
from models.Resources.Tile import Tile
from models.Resources.Terrain_type import Terrain_type

class Map:
    def __init__(self, largeur, hauteur, type_carte="ressources_generales"):
        self.largeur = largeur
        self.hauteur = hauteur
        self.grille = [[None for _ in range(hauteur)] for _ in range(largeur)]
        self.generer_aleatoire(type_carte)
    
    def generer_aleatoire1(self, type_carte="ressources_generales"):
        for x in range(self.largeur):
            for y in range(self.hauteur):
                if random.random() < 0.1:  # 10% pour l'eau
                    terrain_type = Terrain_type.WATER
                else:
                    terrain_type = Terrain_type.GRASS
                self.grille[x][y] = Tile(x, y, terrain_type)

    def generer_aleatoire(self, type_carte="ressources_generales"):
        """Génère une carte où toutes les tuiles sont de type GRASS."""
        for x in range(self.largeur):
            for y in range(self.hauteur):
                self.grille[x][y] = Tile(x, y, Terrain_type.GRASS)



    def __repr__(self):
        return f"Map({self.largeur}x{self.hauteur})"
