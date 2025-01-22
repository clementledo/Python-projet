from models.map_KHANHNGUYEN import Map
from ai_begin_phase import IA

game_map = map(10,10)

gstate = game_state()

gstate.model['map'] = game_map

IA1 = IA(1,gstate)

IA1.initialize_starting_assets(2, 4)

