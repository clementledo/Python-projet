from models.game import Game
from models.Player.player import Player

game = Game(50, 50, "Marines", "central_gold")
game.display()

# Player 1 turn
print("Player 1 turn")
game.players[0].play_turn(game.map, enemy_players=[game.players[1]])
game.update()
game.display()

# Player 2 turn (AI)
print("Player 2 turn")
game.players[1].play_turn(game.map, enemy_players=[game.players[0]])
game.update()
game.display()

# Player 1 turn
print("Player 1 turn")
game.players[0].play_turn(game.map, enemy_players=[game.players[1]])
game.update()
game.display()

# Player 2 turn (AI)
print("Player 2 turn")
game.players[1].play_turn(game.map, enemy_players=[game.players[0]])
game.update()
game.display()