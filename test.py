from map import Map
from resource.tile import Type
from unit.villager import Villager
from building.town_hall import TownHall
from ai import IA

game_map = Map(60, 60)

game_map.generer_aleatoire(type=2)

game_map.display()






