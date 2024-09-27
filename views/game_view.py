import pygame

class GameView:
    def __init__(self, screen, tile_size=32):
        self.screen = screen
        self.unit_sprites = {}  # Dictionnaire pour stocker les images des unités
        self.tile_size = tile_size  # Taille de chaque tuile en pixels

    
    def render_map(self, carte, camera_x, camera_y):
       
        """Affiche la carte en fonction de la position de la caméra."""
        # Calcule combien de tuiles peuvent être visibles à l'écran
        tiles_visible_x = self.screen.get_width() // self.tile_size
        tiles_visible_y = self.screen.get_height() // self.tile_size

        tile_width = self.tile_size * 2  # Largeur isométrique (64 px par ex.)
        tile_height = self.tile_size     # Hauteur isométrique (32 px par ex.)


        # Indices des tuiles visibles sur la carte
        start_tile_x = camera_x // self.tile_size
        start_tile_y = camera_y // self.tile_size
        end_tile_x = min(start_tile_x + tiles_visible_x + 1, carte.largeur)
        end_tile_y = min(start_tile_y + tiles_visible_y + 1, carte.hauteur)
        
        
        for x in range(start_tile_x,end_tile_x):
            for y in range(start_tile_y,end_tile_y):
                
                    tuile = carte.grille[x][y]

                    # Conversion des coordonnées grille vers isométrique
                    iso_x = (x - y) * tile_width // 2 + camera_x
                    iso_y = (x + y) * tile_height // 2 + camera_y

                    if tuile.tile_type == 0:
                        color = (34, 139, 34)  # Vert pour les plaines
                    elif tuile.tile_type == 1:
                        color = (139, 69, 19)  # Marron pour les forêts
                    elif tuile.tile_type == 3:
                        color = (255, 215, 0)  # Jaune pour l'or  
                    else:
                        color = (128, 128, 128)  # Gris pour les montagnes
                    
                    
    
                    
                    # Ne dessiner que les tuiles visibles à l'écran
                    if -tile_width < iso_x < self.screen.get_width() and -tile_height < iso_y < self.screen.get_height():
                        # Dessiner les tuiles sous forme de polygones isométriques
                        pygame.draw.polygon(self.screen, color, [
                            (iso_x, iso_y + tile_height // 2),                # Sommet haut
                            (iso_x + tile_width // 2, iso_y),                 # Coin droit
                            (iso_x + tile_width, iso_y + tile_height // 2),   # Coin bas
                            (iso_x + tile_width // 2, iso_y + tile_height)    # Coin gauche
                        ])
                    
                    
    
    def load_unit_sprite(self, unit_type, image_path):
        """Charger et stocker l'image des unités"""
        image = pygame.image.load(image_path)
        self.unit_sprites[unit_type] = image

    def render_unit(self, unit):
        """Affiche une unité à sa position en mode isométrique"""
        tile_width = self.tile_size * 2  # Largeur isométrique (par ex. 64 pixels)
        tile_height = self.tile_size     # Hauteur isométrique (par ex. 32 pixels)

        # Conversion des coordonnées de l'unité en isométrique
        iso_x = (unit.x - unit.y) * tile_width // 2 - self.camera_x
        iso_y = (unit.x + unit.y) * tile_height // 2 - self.camera_y

        # Récupérer le sprite de l'unité
        sprite = self.unit_sprites.get(unit.unit_type)
        if sprite:
            # Ne dessiner que si l'unité est visible à l'écran
            if -tile_width < iso_x < self.screen.get_width() and -tile_height < iso_y < self.screen.get_height():
                # Centrer le sprite sur la position isométrique de l'unité
                self.screen.blit(sprite, (iso_x - sprite.get_width() // 2, iso_y - sprite.get_height() // 2))
        else:
            print(f"Aucune image trouvée pour {unit.unit_type}")


    def render_background(self, color=(255, 255, 255)):
        """Remplir l'écran avec une couleur de fond"""
        self.screen.fill(color)
    
    def update_display(self):
        """Mettre à jour l'affichage"""
        pygame.display.flip()
    



