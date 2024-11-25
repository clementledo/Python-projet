from map import Map
from resource.tile import Type
from unit.villager import Villager
from building.town_hall import TownHall
from ai import IA

game_map = Map(10, 10)

# Place some terrain tiles
game_map.place_tile(2, 3, Type.Wood)
game_map.place_tile(4, 5, Type.Food)
game_map.place_tile(7, 8, Type.Gold)



ai_1 = IA([],game_map)
ai_1.initialize_starting_assets(0, 0)
ai_2 = IA([],game_map)
ai_2.initialize_starting_assets(8, 8)

all_units = []

for unit in ai_1.units:
    all_units.append(unit)
for unit in ai_2.units:
    all_units.append(unit)

i= 0
game_map.display()
running = True

while running:
    print(f"Cycle {i}:")
    i += 1
    # AI makes decisions for each unit (attack enemies or gather resources)
    ai_1.make_decision(all_units)
    ai_2.make_decision(all_units)
    
    for unit in all_units: 
        if unit.health <= 0:
            all_units.remove(unit)
            if unit in ai_1.units:
                ai_1.units.remove(unit)
            elif unit in ai_2.units:
                ai_2.units.remove(unit)
    
    game_map.display()

    # Break condition for game loop
    if all(enemy.health <= 0 for enemy in all_units if enemy not in ai_1.units) \
        or all(enemy.health <= 0 for enemy in all_units if enemy not in ai_2.units):
        running = False


