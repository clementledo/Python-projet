from models.Resources.map import Map
from models.Units.villager import Villager
from models.Resources.tile import Tile
from models.Resources.resource import Resource
from models.Resources.resource import ResourceType
from models.Buildings.camp import Camp
from models.Units.archer import Archer

map = Map.generate_random_map(120, 120, "default")
map.set_tile(3, 0, Tile((3, 0),None, Resource(ResourceType.GOLD, 800)))
unit1 = Villager((0, 0))
print(unit1)
unit1.move(map, (2, 0))
print(unit1)
camp = Camp((12,12))
map.add_building(camp,12,12)
archer = Archer((0,0))
print(archer)
archer.move(map, (1,1))
archer.attack_unit(unit1)
print(unit1)
archer.attack_unit(unit1)
print(unit1)
archer.attack_unit(unit1)
print(unit1)
