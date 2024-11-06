# Python-projet
Projet python du 1er semestre de 3A à l'INSA CVL. 

Le but est de développer le jeu "Age of Empire". Le jeu est développé en python et ne peux être joué que par deux IA sur 2 sorties différentes :  
- terminale
- 2.5D


```mermaid
---
title: Diagram UML of the Model
---
classDiagram
  class Ressource{
    - Enum~Type~ type
    - int quantity
    - char symbol
    + Ressource(type,symbol, quantity)
  }

  class Type{
    <<enumeration>>
    Gold
    Wood
  }

class Tile{
  - (int,int) position
  - Ressource ressource
  + Tile(position,ressource)
}

note for Tiles "Un composition indique que si l'objet Tile est détruit alors l'objet Ressource associé est aussi détruit. Ici la ressource dépend de la case ou il est."

Ressource  --  Type
Tile --* Ressource : composition

class Building{
  - int cost
  - int size: int
  - Pos pos
  - int hp
  - float build_time
  - char symbol: char
  - int etat

  + void Building()
  + void update()
  + void destroy()
  + int damage(unit: Unit)
}

class Towncentre{

  + void add_resources()
  + void remove_resources()
  + void towncentre()

}
class House{
  + void house()
}
class Camp{
  + void camp()
}
class Farm{
  - int const stockage = 300 

  + void product()

}
class Barracks{
  + void create_swordsman()
}
class Stable{
  + void create_horseman()
}
class Archery_Range{
  + void create_archery()
}
class Keep{
  - int const attack = 5
  - int const range = 8

  + void Keep()
  + void attack()
}
  
Building <|-- Keep
Building <|-- Archery_Range
Building <|-- Stable
Building <|-- Barracks
Building <|-- Farm
Building <|-- Camp
Building <|-- House
Building <|-- Towncentre

class Unit {
  - int cost
  - time trainingTime
  - int hpMax
  - float speedatk
  - float speeddep
  - char symbol
  - int attack
  - int hp
  - Pos position
  
  + void init()
  + int getHp()
  + Pos getPos()
  + void hpLoss(amount: int)
  + void die()
  + void move(position: Pos)
  + void create_path(pos: Pos)
}

class Villager{
  + void collect(Resource resource)
  + void dropResources()
  + void build(Building building)
}

class Swordsman{
  + void attack_sword(target: Unit)
}

class Horseman{
  + void attack_horse(target: Unit)
}

class Archer{
  + void attack_archer(target: Unit)
}

Unit <|-- Villager
Unit <|-- Swordsman
Unit <|-- Horseman
Unit <|-- Archer

```
