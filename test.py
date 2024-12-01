from models.map import Map

#def main():

carte = Map(120, 120)
carte.generer_aleatoire(type_carte="centre_ressources")
for y in range(carte.hauteur):
    print(" ".join([tile.resource[0] if tile.resource else " " for tile in carte.grille[y]]))
