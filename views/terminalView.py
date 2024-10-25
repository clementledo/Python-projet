
from models.unit import Villager


class TerminalView:
    def __init__(self, carte):
        self.carte = carte

    def display_map(self, units):
        """Affiche la carte dans le terminal avec les unités."""
        for y in range(self.carte.hauteur):
            row = ""
            for x in range(self.carte.largeur):
                tuile = self.carte.grille[x][y]
                # Représentation des tuiles
                if tuile.tile_type == 0:
                    row += 'F'  # Ferme
                elif tuile.tile_type == 1:
                    row += 'W'  # bois
            
                elif tuile.tile_type == 2:
                    row += 'G'  # Mine d'or

                unit_here = False
                
                for unit in units:
                    if int(unit.x) == x and int(unit.y) == y:
                        char = 'U'  # U pour unité (vous pouvez changer selon le type d'unité)
                        unit_here = True
                        break
                
                # Représentation des unités
                for unit in units:
                    if unit.x == x and unit.y == y:
                        if isinstance(unit, Villager):
                            row = row[:-1] + 'v'  # Remplacer la tuile par 'v'
                

                
            print(row)  # Affiche la ligne de la carte
