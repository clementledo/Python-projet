import pygame
from views.menu import main_menu, pause_menu, settings_menu
from game_state import GameState
from models.map import Map
from views.game_view import GameView
from models.Player.ai_begin_phase import IA
from models.Buildings.town_center import Town_center
from models.units.villager import Villager  

game = GameState()
carte = Map(100,100)

town = Town_center((10,10))
town2 = Town_center((10,20))

carte.place_building(town2)

villa = Villager(10,30,carte)
villa.move_toward((10,10),carte)
print(villa.current_path)
