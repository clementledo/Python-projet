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

class Tiles{
  - (int,int) position
  - Ressource ressource
  + Tiles(position,ressource)

Ressource  --  Type
Tiles --\* Ressource 
  
```
