```mermaid
classDiagram
    class Game {
        +map: Map
        +players: List[Player]
        +current_state: GameState
        +save()
        +load()
        +start_game()
        +pause()
        +resume()
    }

    class Resource {
        <<enumeration>>
        WOOD
        FOOD
        GOLD
    }

    class Terrain_type {
        <<enumeration>>
        MINTAIN
        PLAINE
        FOREST
    }

    class Map {
        +size_x: int
        +size_y: int
        +tiles: List[Tile]
        +generate_map()
        +get_tile(x, y): Tile
    }

    class Tile {
        +x: int
        +y: int
        +terrain_type: Terrain_type
        +resource: ResourceTile
        +occupant: Unit | Building | None
    }

    class ResourceTile {
        +type: Resource
        +amount: int
        +max_amount: int
        +depleted: bool
        +deplete()
        +harvest(amount: int): int
    }

    class Player {
        <<abstract>>
        +name: str
        +resources: Dict[Resource, int]
        +population_current: int
        +population_max: int
        +units: List[Unit]
        +buildings: List[Building]
        +add_unit(unit: Unit)
        +remove_unit(unit: Unit)
        +update_resources(resource: Resource, amount: int)
        +can_afford(cost: Dict[Resource, int]): bool
    }

    class HumanPlayer

    class AIPlayer {
        -strategy: GameStrategy
        -knowledge_base: GameState
        +plan_strategy()
        +evaluate_game_state()
        +make_decision(): PlayerAction
        +update_strategy(game_state: GameState)
        +choose_build_order()
        +manage_resource_allocation()
        +micro_manage_units()
    }

    class GameStrategy {
        <<abstract>>
        +aggressive
        +defensive
        +economic
        +rush_strategy
    }

    class PlayerAction {
        +type: ActionType
        +target: Unit | Building | Tile
        +parameters: Dict
    }

    class ActionType {
        <<enumeration>>
        MOVE
        ATTACK
        BUILD
        GATHER
        RESEARCH
    }

    class Unit {
        <<abstract>>
        +hp: int
        +attack: int
        +speed: float
        +cost: Dict[Resource, int]
        +position: Tuple[int, int]
        +symbol: char
        +attack_speed: float
        +move(destination: Tuple[int, int])
        +attack(target: Unit)
    }

    class Villager {
        +void build(building: Building)
        +void collect_resource(resource_type: Resource)
        +carry_capacity: int
        +collection_rate: float
        +drop_resources()
    }

    class Swordsman 
    class Horseman 
    class Archer {
        +range: int
    }

    class Building {
        <<abstract>>
        +hp: int
        +position: Tuple[int, int]
        +cost: Dict[Resource, int]
        +build_time: int
        +symbol: char
        +size: Tuple[int, int]
    }

    class TownCentre {
        +spawn_villager()
  
    }

    class House {
        # Population increase functionality
    }

    class Farm

    class Camp {
      
    }
    class MilitaryBuilding {
        <<abstract>>
        +spawn_unit()
    }

    class Barracks {
        +spawn_swordsman()
    }

    class Stable {
        +spawn_horseman()
    }

    class ArcheryRange {
        +spawn_archer()
    }

    class Keep {
        +fire_arrows()
    }

    Game "1" *-- "1..*" Player
    Game "1" *-- "1" Map
    Map "1" *-- "many" Tile
    Tile "1" *-- "0..1" ResourceTile
    Player "1" *-- "many" Unit
    Player "1" *-- "many" Building

    Unit <|-- Villager
    Unit <|-- Swordsman
    Unit <|-- Horseman
    Unit <|-- Archer

    Building <|-- TownCentre
    Building <|-- House
    Building <|-- Farm
    Building <|-- Camp
    Building <|-- MilitaryBuilding
    Building <|-- Keep
    Farm <|-- ResourceTile

    MilitaryBuilding <|-- Barracks
    MilitaryBuilding <|-- Stable
    MilitaryBuilding <|-- ArcheryRange

    Player <|-- HumanPlayer
    Player <|-- AIPlayer
    Player --> Unit
    Player --> Building
    AIPlayer *-- GameStrategy
    AIPlayer -- PlayerAction : generates
    PlayerAction -- ActionType

    %% note ResourceTile: Wood (W): 100 per tile\nFood (F): 300 per farm\nGold (G): 800 per tile
```
