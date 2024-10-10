import random

"""classe Tile pas utile je pense (pour la vue terminale)"""
class Tile:
    """Classe représentant une seule tuile."""
    def __init__(self, tile_type):
        self.tile_type = tile_type  # Type de tuile (eau, plaine, forêt, etc.)

class Carte:
    """Classe représentant la carte sous forme de grille N x M."""
    def __init__(self, largeur, hauteur):
        self.largeur = largeur
        self.hauteur = hauteur
        self.grille = [[None for _ in range(hauteur)] for _ in range(largeur)]

    def generer_aleatoire(self,type_carte="ressources_generales"):
        """Génère une carte aléatoire en remplissant la grille avec des tuiles aléatoires."""
        for x in range(self.largeur):
            for y in range(self.hauteur):
                # Choisir un type de tuile aléatoire, par exemple : 0 = plaine, 1 = forêt, 2 = montagne
                if type_carte == "ressources_generales":
                    """tile = random.choice(['W','T','G', 'F','v'])"""
                    tile_type = random.choice([0, 1, 2])  # Plain, forêt, montagne
                elif type_carte == "or_central":
                    if 40 < x < 80 and 40 < y < 80:  # Mettons que l'or est concentré au centre
                        """tile='G'"""
                        tile_type = 3  # Type spécial pour l'or
                    else:
                        """tile = random.choice(['W','T','G', 'F','v'])"""
                        tile_type = random.choice([0, 1, 2])
                """self.grille[x][y] = tile"""
                self.grille[x][y] = Tile(tile_type)
