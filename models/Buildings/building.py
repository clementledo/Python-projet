"""utilisation des mÃ©thodes dans la classe Joueur (IA)"""
import pygame
import time

from views.asset_manager import AssetManager

class Building :
    def __init__(self, name, construction_time, hp, size, symbol, pos) :
        self.cost = {"wood":0,"gold":0}
        self.construction_time = construction_time
        self.hp = hp
        self.health = hp
        self.symbol = symbol
        self.size = size
        self.pos = pos
        self.position = pos
        self.name=name
        self.counter=0
        self.curr_tick=0
        self.asset_manager = AssetManager()
        self.image = self.asset_manager.get_building_sprite(name)
        self.useable=True
        self.player_id = None
        self.builder = []
        #self.state = state
        
    """bÃ¢timent construit par 1 ou plusieurs villageois"""
    """bÃ¢timent construit par 1 villageois -> nominal_construction_time"""
    """bÃ¢timent construit par pls villageois -> (3 * nominal_construction_time) / (builders_count + 2)"""
    
    def building(self, builders) :
        self.useable = False
        for builder in builders :
            builder.is_building = True
            self.builder.append(builder)
        self.construction_time = (3 * self.construction_time) / (len(builders) + 2)
        print(f"Construction commencÃ©e. Temps de construction rÃ©el : {self.construction_time} secondes.")
        self.construction_start_time = time.time()  # Log the current time


    def update(self):
        """Met à jour la progression de la construction du bâtiment."""
        if not self.useable:  # Si le bâtiment n'est pas encore utilisable
            self.curr_tick += 1

            # Vérifiez si un intervalle de construction est atteint
            if self.curr_tick >= self.construction_time:
                self.counter += 1
                self.curr_tick = 0  # Réinitialisez le tick courant

                # Appeler la méthode pour changer l'image selon le stade
                self.in_construction(self.size)

    def check_construction(self):
        if not self.useable:
            elapsed_time = time.time() - self.construction_start_time
            if elapsed_time >= self.construction_time:
                self.useable = True
                print(f"{self.name} is fully constructed!")
            #else:
                #print(f"{self.name} is still under construction...")
                #print(f"Elapsed time: {elapsed_time} seconds")
    
    def destroy(self) :
        self.health = 0
        self.set_broken()
        
    def take_damage(self, atk) :
        self.health -=  atk
        if self.health <= 0 :
            self.destroy()
        print(f"{self.name} has {self.health} HP left.")

    def print_building(self) :
        print(self.symbol)

    def worksite(self, size) :
        return pygame.image.load("assets/Buildings/in_construction/1X1/while_building_1_1.png")


    def in_construction(self, size):
        """Met à jour l'image en fonction de l'état de construction."""
        if self.counter == 1:
            self.image = pygame.image.load(f"assets/Buildings/in_construction/1X1/while_building_1_2.png")
        elif self.counter == 2:
            self.image = pygame.image.load(f"assets/Buildings/in_construction/1X1/while_building_1_3.png")
        elif self.counter >= 3:
            self.image = pygame.image.load(f"assets/Buildings/{self.name}.png")
            self.useable = True
            self.curr_tick = 0  # Réinitialiser les ticks pour des actions futures

    def is_idle(self):
        return self.useable

    def broken(self, size) :
        return self.asset_manager.get_broken_building_sprite(size)

    def set_broken(self):
        """Marquer le bâtiment comme cassé et changer l'image."""
        self.image = self.broken(self.size)
        self.useable = False  # Le bâtiment devient inutilisable

    def serialize(self):
        """Retourne une version sérialisable du bâtiment."""
        return {
            "name": self.name,
            "size": self.size,
            "cost": self.cost,
            "construction_time": self.construction_time,
            "hp": self.hp,
            "useable": self.useable,
            "symbol": self.symbol,
            "pos": self.pos,
            "player_id": self.player_id if hasattr(self, 'player_id') else None
        }
    
    @classmethod
    def deserialize(cls, data):
        """Recrée un bâtiment à partir des données sérialisées."""
        building = cls(data["name"],data["size"],data["cost"],data["construction_time"],data["hp"],  data["symbol"] ,data["pos"])
        building.useable = data["useable"]
        building.image = building.asset_manager.get_building_sprite(data['name'])
        return building

