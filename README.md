# Jeu de Simulation

## Deux versions fonctionnelles du jeu :

### 2.5D : `game_view.py` & `main.py`

- Déplacement avec les touches fléchées et la souris
- Zoom avec la molette
- Reste à ajouter les ressources dans le jeu (icônes avec les statistiques / tuiles)

#### Gestion des touches :
- `ESC` : Pause
- Bouton `Load Game` à corriger...

### Terminal : `terminal_view.py` & `main2.py`

- Les bâtiments en violet
- Les unités en bleu
- Les ressources en jaune

#### Gestion des touches :
- `ZQSD` : Bouger
- `P` : Pause
- `TAB` : Statistiques
- `Q` : Quitter

- Page HTML à faire avec les statistiques (à faire...)

## Intégration du vrai jeu avec les IA...


# Python-projet

main.py: Le jeu principal

test.py: Tester les nouvelles fonctions

Les fonctions ajoutées:

    unit:
    Les fonctions pour trouver le chemin
    Les fonctions pour mettre a jour dans la carte

    building:
    Les fonctions pour mettre a jour dans la carte

    resource:
    tile.py:
    Les fonctions pour ajouter/supprimer des units

map.py: 

    La carte
    Les fonctions pour m.a.j
    Une fonction pour afficher dans le terminal
    une fonction pour générer aléatoire

ai.py:

    logique pour l'IA
    les fonctions déja testé:
        make_decision
        find_nearby_targets
        find_nearby_resources
        les fonctions concernant le chemin
        les fonction pour construire les batiments
