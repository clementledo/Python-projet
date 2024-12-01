class TerminalView:
    def __init__(self, game_state, tile_size=1):
        self.game_state = game_state
        self.tile_size = tile_size
        self.camera_x = 0
        self.camera_y = 0
        self.speed = 1  # Défilement rapide
        self.pause = False

    def render_map(self):
        """Affiche la carte dans le terminal."""
        carte = self.game_state.carte
        units = self.game_state.model['units']
        buildings = self.game_state.model['buildings']
        
        # Codes de couleur ANSI
        COLORS = {
            "reset": "\033[0m",
            "building": "\033[35m",  # Violet pour les bâtiments
            "unit": "\033[32m",      # Vert pour les unités
            "resource": "\033[33m"   # Jaune pour les ressources
        }
        
        # Créer une grille vide
        grille = [["  " for _ in range(carte.largeur)] for _ in range(carte.hauteur)]
        
        # Placer les ressources sur la carte (sans afficher les types de terrain)
        for y in range(len(carte.grille)):
            for x in range(len(carte.grille[0])):
                if carte.grille[y][x].resource:
                    grille[y][x] = COLORS["resource"] + carte.grille[y][x].resource.symbol + COLORS["reset"]

        # Placer les bâtiments sur la grille
        for building in buildings:
            x, y = building.pos
            width, height = building.size  # Taille du bâtiment (largeur, hauteur)
            symbol = building.symbol

            # Remplir toutes les cases occupées par le bâtiment
            for i in range(height):
                for j in range(width):
                    bx, by = x + j, y + i  # Calcul des coordonnées
                    if 0 <= bx < carte.largeur and 0 <= by < carte.hauteur:
                        grille[by][bx] = COLORS["building"] + symbol + COLORS["reset"]

        # Placer les unités sur la grille
        for unit in units:
            x, y = unit.position
            symbol = unit.symbol
            if 0 <= x < carte.largeur and 0 <= y < carte.hauteur:
                grille[y][x] = COLORS["unit"] + symbol + COLORS["reset"]

        # Afficher la grille avec la caméra
        visible_rows = grille[self.camera_y:self.camera_y + 30]  # 30 lignes visibles
        for row in visible_rows:
            print("  ".join(row[self.camera_x:self.camera_x + 40]))  # 50 colonnes visibles


    def handle_input(self):
        """Gère les entrées utilisateur."""
        command = input("Commande (ZQSD: bouger, P: pause, TAB: stats, Q: quitter) : ").lower()
        
        if command == "z":
            self.camera_y = max(0, self.camera_y - self.speed)
        elif command == "s":
            self.camera_y = min(self.game_state.carte.hauteur - 20, self.camera_y + self.speed)
        elif command == "q":
            self.camera_x = max(0, self.camera_x - self.speed)
        elif command == "d":
            self.camera_x = min(self.game_state.carte.largeur - 40, self.camera_x + self.speed)
        elif command == "p":
            self.pause = not self.pause
            print("Jeu en pause." if self.pause else "Jeu repris.")
        elif command == "tab":
            self.render_game_stats()
        elif command == "quit" or command == "q":
            print("Quitter le jeu. À bientôt !")
            exit()
        else:
            print("Commande inconnue.")

    def run(self):
        """Boucle principale de la vue terminale."""
        print("=== Bienvenue dans le jeu en mode terminal ===")
        print("Utilisez ZQSD pour bouger la caméra, P pour mettre en pause, TAB pour voir les stats, et Q pour quitter.\n")
        
        while True:
            if not self.pause:
                self.render_map()
            self.handle_input()
