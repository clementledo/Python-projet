from models.Resources.map import Map
from models.Player.player import Player
from models.Buildings.towncenter import TownCenter
from models.Buildings.barrack import Barrack
from models.Units.villager import Villager
from models.Buildings.archery_range import ArcheryRange
from models.Buildings.stable import Stable
from models.Resources.resource_type import ResourceType
import threading

STARTING_CONDITIONS = {
    "Maigre": {
        "resources": {ResourceType.FOOD: 50, ResourceType.WOOD: 200, ResourceType.GOLD: 50},
        "buildings": ["TownCenter"],
        "units": ["Villager", "Villager", "Villager"]
    },
    "Moyenne": {
        "resources": {ResourceType.FOOD: 2000, ResourceType.WOOD: 2000, ResourceType.GOLD: 2000},
        "buildings": ["TownCenter"],
        "units": ["Villager", "Villager", "Villager"]
    },
    "Marines": {
        "resources": {ResourceType.FOOD: 20000, ResourceType.WOOD: 20000, ResourceType.GOLD: 20000},
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
    def __init__(self, width, height, starting_condition="Maigre", map_type="default"):
        self.map = Map(width, height)
        self.players = []
        self.add_player(Player(1), starting_condition)
        self.add_player(Player(2), starting_condition)
        self.map_type = map_type
        self.map.add_resources(self.map_type)

    def add_player(self, player: Player, starting_condition="Maigre", general_strategy="balanced"):
        player.general_strategy = general_strategy
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
            offset_x, offset_y = self.map.width - 6, self.map.height - 6
            if condition_name == "Marines":
                offset_x, offset_y = self.map.width - 15, self.map.height - 15
        else:
            offset_x, offset_y = 0, 0  # Default to top left if player id is not 1 or 2

        if condition_name in ["Maigre", "Moyenne"]:
            max_width, max_height = 7, 7
        elif condition_name == "Marines":
            max_width, max_height = 15, 15
        else:
            max_width, max_height = self.map.width, self.map.height

        for building_name in condition["buildings"]:
            position = self._find_valid_position(offset_x, offset_y, building_name, max_width, max_height)
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
            position = self._find_valid_position_for_unit(offset_x, offset_y, max_width, max_height)
            if unit_name == "Villager":
                unit = Villager(position=position)
            # Add other unit types here
            self.map.add_unit(unit)
            player.add_unit(unit)

    def _find_valid_position(self, offset_x, offset_y, name, max_width, max_height):
        size = {"TownCenter": (4, 4), "Barrack": (3, 3), "ArcheryRange": (3, 3), "Stable": (3, 3)}.get(name, (1, 1))
        for dx in range(offset_x, min(offset_x + max_width, self.map.width) - size[0] + 1, size[0] + 1):
            for dy in range(offset_y, min(offset_y + max_height, self.map.height) - size[1] + 1, size[1] + 1):
                if all(self.map.get_tile(dx + j, dy + i).occupant is None and not self.map.get_tile(dx + j, dy + i).has_resource() for i in range(size[1]) for j in range(size[0])):
                    return (dx, dy)
        raise ValueError("No valid position available")

    def _find_valid_position_for_unit(self, offset_x, offset_y, max_width, max_height):
        for dx in range(offset_x, min(offset_x + max_width, self.map.width)):
            for dy in range(offset_y, min(offset_y + max_height, self.map.height)):
                if self.map.get_tile(dx, dy).occupant is None:
                    return (dx, dy)
        raise ValueError("No valid position available")

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

    def play_turn(self):
        threads = []
        for player in self.players:
            enemy_players = [p for p in self.players if p != player]
            thread = threading.Thread(target=player.play_turn, args=(self.map, enemy_players))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

    def check_game_over(self):
        for player in self.players:
            if not player.buildings:
                winner = [p for p in self.players if p != player][0]
                print(f"Player {winner.player_id} wins!")
                return True
            elif not player.units and player.resources[ResourceType.FOOD] < 50:
                winner = [p for p in self.players if p != player][0]
                print(f"Player {winner.player_id} wins!")
                return True
            print(f"Player {player.player_id} has {len(player.buildings)} buildings and {len(player.units)} units")
        return False
