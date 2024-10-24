from unit.unit import Unit
from unit.villager import Villager
from ai import IA
from map import Map
from resource.tile import Type


game_map = Map(10, 10)

# Place some terrain tiles
game_map.place_tile(2, 3, Type.Wood)
game_map.place_tile(4, 5, Type.Food)
game_map.place_tile(7, 8, Type.Gold)
# Define units controlled by AI
unit1 = Unit(0, 0, "warrior1",5, 1.2, 25, game_map)
unit2 = Villager(1, 1, game_map)
enemy1 = Unit(4, 4, "warrior2",5,0.5,20, game_map)
enemy2 = Unit(4, 3, "warrior3",5,0.8,15, game_map)
# AI controls these units
units_controlled_by_ai_1 = [unit1, unit2]
units_controlled_by_ai_2= [enemy1, enemy2]

# All units on the map, including AI-controlled and enemies
all_units = [unit1, unit2, enemy1, enemy2]  # Example list of units

# Create AI controller
ai_1 = IA(units_controlled_by_ai_1, game_map)
ai_2 = IA(units_controlled_by_ai_2, game_map)

i = 0

# Game loop
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
            if unit in units_controlled_by_ai_1:
                units_controlled_by_ai_1.remove(unit)
            elif unit in units_controlled_by_ai_2:
                units_controlled_by_ai_2.remove(unit)
    
    game_map.display()

    # Break condition for game loop
    if all(enemy.health <= 0 for enemy in all_units if enemy not in units_controlled_by_ai_1) \
        or all(enemy.health <= 0 for enemy in all_units if enemy not in units_controlled_by_ai_2):
        running = False

