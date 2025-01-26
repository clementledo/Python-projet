from models.game import Game
from models.Player.player import Player

game = Game(50,50, "Marines","central_gold")
game.update()

game.display()