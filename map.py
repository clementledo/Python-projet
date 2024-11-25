import random
import os
import platform


class Tile:
    """Classe représentant une seule tuile."""
    def __init__(self, tile_type):
        self.tile_type = tile_type  # Type de tuile (eau, plaine, forêt, etc.)

    def get_color(self):
        """Retourne la couleur associée au type de ressource."""
        if self.tile_type == 0:  # Type bois
            return (34, 139, 34)  # Vert foncé
        elif self.tile_type == 2:  # Type nourriture
            return (139, 69, 19)  # Marron
        elif self.tile_type == 1:  # Type or
            return (255, 215, 0)  # Doré
        else:
            return (128, 128, 128)  # Couleur par défaut (gris) si le type n'est pas reconnu

class Map:
    """Classe représentant la carte sous forme de grille N x M."""
    def __init__(self, largeur, hauteur):
        self.largeur = largeur
        self.hauteur = hauteur
        self.grille = [[None for _ in range(hauteur)] for _ in range(largeur)]

    def generer_aleatoire(self, type_carte="ressources_generales"):
        """Génère une carte aléatoire avec 50% de tuiles vides, sans nourriture."""
        for x in range(self.largeur):
            for y in range(self.hauteur):
                if random.random() < 0.5:
                    tile_type = 3  # Tuile vide
                else:
                    if type_carte == "ressources_generales":
                        tile_type = random.choice([0, 1])  # wood, gold
                    elif type_carte == "or_central":
                        if 40 < x < 80 and 40 < y < 80:  # Mettons que l'or est concentré au centre
                            tile_type = 1  # Type spécial pour l'or
                        else:
                            tile_type = random.choice([0, 1])
                self.grille[x][y] = Tile(tile_type)

    def afficher_terminal(self):
        """Affiche la carte dans le terminal."""
        print("Carte de la region: \n")
        for y in range(self.hauteur):
            ligne = ''
            for x in range(self.largeur):
                tile = self.grille[x][y]
                if tile.tile_type == 0:
                    symbole = 'W'  # Bois
                elif tile.tile_type == 1:
                    symbole = 'G'  # Or
                elif tile.tile_type == 3:
                    symbole = ' '  # Tuile vide
                else:
                    symbole = '?'
                ligne += symbole
            print(ligne)