from models.game import Game
from models.Player.player import Player

game = Game(50,50, "Moyenne","central_gold")
game.update()

game.display()