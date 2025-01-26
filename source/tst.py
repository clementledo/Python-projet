from models.game import Game
from models.Player.player import Player

game = Game(120,120)
game.add_player(Player(1),"Marines")
game.add_player(Player(2),"Marines")
game.update()

game.display()