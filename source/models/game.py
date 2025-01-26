from models.Resources.map import Map
from models.Player.player import Player
from models.Buildings.towncenter import TownCenter
from models.Buildings.barrack import Barrack
from models.Units.villager import Villager
from models.Buildings.archery_range import ArcheryRange
from models.Buildings.stable import Stable

STARTING_CONDITIONS = {
    "Maigre": {
        "resources": {"Food": 50, "Wood": 200, "Gold": 50},
        "buildings": ["TownCenter"],
        "units": ["Villager", "Villager", "Villager"]
    },
    "Moyenne": {
        "resources": {"Food": 2000, "Wood": 2000, "Gold": 2000},
        "buildings": ["TownCenter"],
        "units": ["Villager", "Villager", "Villager"]
    },
    "Marines": {
        "resources": {"Food": 20000, "Wood": 20000, "Gold": 20000},
        "buildings": [
            "TownCenter",    # Main town center
            "Barrack",       # Barrack near the center
            "ArcheryRange",  # Archery range near the center
            "TownCenter",    # Secondary town center left
            "Barrack",       # Support barrack
            "TownCenter",    # Secondary town center right
            "ArcheryRange",   # Support archery range
            "Stable",        # Stable near the center
            "Stable"         # Support stable
        ],
        "units": ["Villager"] * 15
    }
}

class Game:
    def __init__(self, width, height, map_type="default"):
        self.map = Map.generate_random_map(width, height, map_type)
        self.players = []

    def add_player(self, player: Player, starting_condition="Maigre"):
        self.players.append(player)
        self._apply_starting_conditions(player, starting_condition)

    def remove_player(self, player: Player):
        self.players.remove(player)

    def _apply_starting_conditions(self, player: Player, condition_name):
        condition = STARTING_CONDITIONS[condition_name]
        for resource, amount in condition["resources"].items():
            player.add_resource(resource, amount)
        
        if player.player_id == 1:
            offset_x, offset_y = 0, 0
        elif player.player_id == 2:
            offset_x, offset_y = self.map.width - 5, self.map.height - 5
        else:
            offset_x, offset_y = 0, 0  # Default to top left if player id is not 1 or 2

        for building_name in condition["buildings"]:
            position = self._find_valid_position(offset_x, offset_y)
            self._clear_resources(position, building_name)
            if building_name == "TownCenter":
                building = TownCenter(position)
            elif building_name == "Barrack":
                building = Barrack(position)
            elif building_name == "ArcheryRange":
                building = ArcheryRange(position)
            elif building_name == "Stable":
                building = Stable(position)
            # Add other building types here
            self.map.add_building(building)
            player.add_building(building)
        
        for unit_name in condition["units"]:
            position = self._find_valid_position(offset_x, offset_y)
            self._clear_resources(position, unit_name)
            if unit_name == "Villager":
                unit = Villager(position=position)
            # Add other unit types here
            self.map.add_unit(unit)
            player.add_unit(unit)

    def _find_valid_position(self, offset_x, offset_y):
        for dx in range(offset_x, self.map.width):
            for dy in range(offset_y, self.map.height):
                if self.map.get_tile(dx, dy).occupant is None:
                    return (dx, dy)
        raise ValueError("No valid position available")

    def _clear_resources(self, position, name):
        x, y = position
        tile = self.map.get_tile(x, y)
        if tile.has_resource():
            tile.resource = None

    def update(self):
        self.map.update()
        for player in self.players:
            for unit in player.units:
                if unit.hp <= 0:
                    player.remove_unit(unit)
            for building in player.buildings:
                if building.hp <= 0:
                    player.remove_building(building)

    def display(self):
        self.map.display()
        for player in self.players:
            print(player)

    def __repr__(self):
        return (f"Game(map={self.map}, players={len(self.players)})")
