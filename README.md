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
    -Enum~Type~ type
    -int quantity
    -char symbol
    +Ressource(type,symbol, quantity)
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
  
```
