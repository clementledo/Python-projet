from models.map_KHANHNGUYEN import Map
from ai_begin_phase import IA

game_map = Map(10,10)

gstate = GameState()

gstate.carte = game_map

IA1 = IA(1,gstate)

IA1.initialize_starting_assets(2, 4)

