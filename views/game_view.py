import pygame

class GameView:
    def __init__(self, screen, tile_size=32):
        self.screen = screen
        self.unit_sprites = {}  # Dictionnaire pour stocker les images des unités
        self.tile_size = tile_size  # Taille de chaque tuile en pixels
         
    
    
    def render_map(self, carte, camera_x, camera_y,zoom_level):
       
        """Affiche la carte en fonction de la position de la caméra."""
        # Calcule combien de tuiles peuvent être visibles à l'écran
        tiles_visible_x = self.screen.get_width() // self.tile_size
        tiles_visible_y = self.screen.get_height() // self.tile_size

        tile_width = self.tile_size * 2 *zoom_level # Largeur isométrique (64 px par ex.)
        tile_height = self.tile_size*zoom_level     # Hauteur isométrique (32 px par ex.)


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
                        color = (34, 139, 34)  # Vert pour wood
                    elif tuile.tile_type == 2:
                        color = (139, 69, 19)  # Marron pour  food
                    elif tuile.tile_type == 1:
                        color = (255, 215, 0)  # Jaune pour gold  
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
                    
                    
    def render_minimap(self, map_data, camera_x, camera_y, zoom_level):
        """Affiche une mini-carte avec un fond et la position de la caméra."""
        # Dimensions de la mini-carte
        minimap_width = 120
        minimap_height = 120
        
        # Position de la mini-carte en bas à droite
        minimap_x = self.screen.get_width() - minimap_width - 20  # Décalé de 20 pixels par rapport au bord
        minimap_y = self.screen.get_height() - minimap_height - 20

        # Dessiner le fond de la mini-carte
        pygame.draw.rect(self.screen, (50, 50, 50), (minimap_x - 5, minimap_y - 5, minimap_width + 10, minimap_height + 10))  # Fond plus grand pour une bordure
        pygame.draw.rect(self.screen, (0, 0, 0), (minimap_x, minimap_y, minimap_width, minimap_height))  # Fond de la mini-carte

        # Calculer la taille d'une tuile sur la mini-carte
        tile_width = minimap_width / map_data.largeur
        tile_height = minimap_height / map_data.hauteur

        # Dessiner les tuiles de la mini-carte
        for x in range(map_data.largeur):
            for y in range(map_data.hauteur):
                tile = map_data.grille[x][y]
                if tile:
                    color = tile.get_color()
                    pygame.draw.rect(self.screen, color, 
                                    (minimap_x + x * tile_width, minimap_y + y * tile_height, 
                                    tile_width, tile_height))

        # Représenter la zone visible sur la mini-carte (rectangle de la caméra)
        map_width_in_pixels = map_data.largeur * self.tile_size
        map_height_in_pixels = map_data.hauteur * self.tile_size

        # Calcul de la taille du rectangle de la caméra sur la mini-carte
        camera_rect_width = (self.screen.get_width() / map_width_in_pixels) * minimap_width / zoom_level
        camera_rect_height = (self.screen.get_height() / map_height_in_pixels) * minimap_height / zoom_level

        # Calcul de la position du rectangle de la caméra sur la mini-carte
        camera_rect_x = minimap_x + (camera_x / map_width_in_pixels) * minimap_width
        camera_rect_y = minimap_y + (camera_y / map_height_in_pixels) * minimap_height

        # Dessiner le rectangle de la caméra
        pygame.draw.rect(self.screen, (255, 0, 0), 
                        (camera_rect_x, camera_rect_y, 
                        camera_rect_width, camera_rect_height), 2)

        # Ajout de quelques icônes (facultatif)
        # Exemple : Afficher des icônes de zoom ou d'autres options
        # Pour cela, il faudra charger les images d'icônes avec pygame.image.load et les afficher avec blit





        

    def load_unit_sprite(self, unit_type, image_path):
        """Charger et stocker l'image des unités"""
        image = pygame.image.load(image_path)
        self.unit_sprites[unit_type] = image

    def render_unit(self, unit,camera_x,camera_y,zoom_level):
        """Affiche une unité à sa position en mode isométrique"""
        tile_width = self.tile_size * zoom_level  # Largeur isométrique (par ex. 64 pixels)
        tile_height = self.tile_size*zoom_level     # Hauteur isométrique (par ex. 32 pixels)

        # Conversion des coordonnées de l'unité en isométrique
        iso_x = (unit.position[0] - unit.position[1]) * (tile_width // 2) 
        iso_y = (unit.position[0] + unit.position[1]) * (tile_height // 2) 
        
        # Ajustement par la position de la caméra
        iso_x -= camera_x
        iso_y -= camera_y

        print(f"Position unitaire: {unit.position} - Iso: ({iso_x}, {iso_y})")
        
        # Limiter les positions isométriques pour s'assurer qu'elles sont visibles
        if iso_x < -tile_width or iso_x > self.screen.get_width() or iso_y < -tile_height or iso_y > self.screen.get_height():
            print(f"Unité hors de l'écran à: ({iso_x}, {iso_y})")
            return  

        # Récupérer le sprite de l'unité
        sprite = self.unit_sprites.get(unit.unit_type)
        if sprite:
            print(f"Affichage de l'unité {unit.unit_type} à la position iso ({iso_x}, {iso_y})")
        

            sprite_scaled = pygame.transform.scale(sprite, (int(sprite.get_width() * zoom_level), int(sprite.get_height() * zoom_level)))
            # Ne dessiner que si l'unité est visible à l'écran
            if 0 <= iso_x <= self.screen.get_width() and 0 <= iso_y <= self.screen.get_height():
                # Centrer le sprite sur la position isométrique de l'unité
                self.screen.blit(sprite_scaled, (iso_x - sprite_scaled.get_width() // 2, iso_y - sprite_scaled.get_height() // 2))
            else:
                print(f"Unité hors de l'écran à: ({iso_x}, {iso_y})")
            
        else:
            print(f"Aucune image trouvée pour {unit.unit_type}")

    # views/game_view.py
    def render_unit2(self, unit, camera_x, camera_y, zoom_level):
        """Affiche une unité en fonction de la caméra et des coordonnées isométriques"""
    
        # Position de l'unité en grille
        x, y = unit.position

        # Largeur et hauteur des tuiles en fonction du zoom
        tile_width = self.tile_size * 2 * zoom_level  # Largeur isométrique
        tile_height = self.tile_size * zoom_level     # Hauteur isométrique

        # Conversion des coordonnées grille vers isométriques
        iso_x = abs(x - y) * (tile_width // 2)
        iso_y = (x - y) * (tile_height // 2)

        # Ajuster la position en fonction de la caméra
        screen_x = iso_x - camera_x
        screen_y = iso_y - camera_y

        # Debugging
        print(f"Position unitaire: {unit.position} - Position écran: ({screen_x}, {screen_y})")

        # Récupérer le sprite de l'unité
        sprite = self.unit_sprites.get(unit.unit_type)
        if sprite:
            # Redimensionner le sprite selon le niveau de zoom
            sprite_scaled = pygame.transform.scale(sprite, (int(sprite.get_width() * zoom_level), int(sprite.get_height() * zoom_level)))
            
            # Vérification si l'unité est visible à l'écran
            if 0 <= screen_x <= self.screen.get_width() and 0 <= screen_y <= self.screen.get_height():
                # Centrer le sprite sur la position de l'unité
                self.screen.blit(sprite_scaled, (screen_x - sprite_scaled.get_width() // 2, screen_y - sprite_scaled.get_height() // 2))
            else:
                print(f"Unité hors de l'écran à: ({screen_x}, {screen_y})")
        else:
            print(f"Aucune image trouvée pour {unit.unit_type}")


    def render_units(self, units, camera_x, camera_y, zoom_level):
        for unit in units:
            self.render_unit2(unit, camera_x, camera_y, zoom_level)

    def render_background(self, img):
        """Remplit l'écran avec une image de fond"""
        # Obtenez les dimensions de l'écran
        screen_width, screen_height = self.screen.get_size()
        
        # Boucle pour remplir l'écran avec l'image en mosaïque (si elle est plus petite que l'écran)
        for x in range(0, screen_width, img.get_width()):
            for y in range(0, screen_height, img.get_height()):
                self.screen.blit(img, (x, y))

    
    def update_display(self):
        """Mettre à jour l'affichage"""
        pygame.display.flip()
    



