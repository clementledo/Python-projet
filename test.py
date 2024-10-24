from map import Map
from resource.tile import Type
from unit.villager import Villager
from building.town_hall import TownHall

game_map = Map(10, 10)

# Place some terrain tiles
game_map.place_tile(2, 3, Type.Wood)
#game_map.place_tile(4, 5, Type.Food)
#game_map.place_tile(7, 8, Type.Gold)


# Create a Town Hall and place it on the map at position (5, 5)
town_hall = TownHall(5, 5, "")

# Attempt to place the Town Hall
try:
    game_map.place_building(town_hall)
except ValueError as e:
    print(e)

# Display the map after placing the Town Hall
game_map.display()
