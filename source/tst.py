from models.Resources.map import Map
from models.Units.villager import Villager
from models.Buildings.camp import Camp
from models.Buildings.farm import Farm

map = Map.generate_random_map(20, 20, "default")
unit1 = Villager((0, 0))
map.add_unit(unit1)
ferme = Farm((1,1))
camp = Camp((5,5))
map.add_building(ferme)
map.add_building(camp)

r = unit1.find_nearest_resource(map)
unit1.move_to(map,r )
map.update()
map.display()

unit1.collect_resource(r,map)
print(r)
map.update()
while map.get_tile(1, 1).occupant == ferme:
    unit1.move_to(map, ferme)
    unit1.collect_resource(map.get_tile(1, 1), map)
    print(unit1)
    unit1.move_to(map, camp)
    map.update()
    print("-------------------------------------------------")
    map.display()
    unit1.drop_resource(map)
    map.update()
map.update()
print("-------------------------------------------------")
map.display()