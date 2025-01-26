from models.game import Game
from models.Player.player import Player

game = Game(50, 50, "Maigre", "central_gold")
game.players[0].general_strategy = "economic"
game.players[1].general_strategy = "aggressive"
game.display()

# Play multiple turns
# for turn in range(100):
#     print(f"Turn {turn + 1}")
while not game.check_game_over():
    game.play_turn()
    game.update()
    game.display()

print("Player 1")
for u in game.players[0].units:
    print(u)
for b in game.players[0].buildings:
    print(b)

print("Player 2")
for u2 in game.players[1].units:
    print(u2)
for b2 in game.players[1].buildings:
    print(b2)