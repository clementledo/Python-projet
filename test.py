from map import Map
from resource.tile import Type
from unit.villager import Villager
from building.town_hall import TownHall
from ai import IA

game_map = Map(10, 10)

#game_map.generer_aleatoire(type=2)

game_map.place_tile(2, 3, Type.Wood)

IA1 = IA([],game_map)

IA1.initialize_starting_assets(0, 0)
available_villagers = IA1.get_available_villagers()
print(available_villagers)
for i in range(5):
    IA1.allocate_villagers()


game_map.display()




