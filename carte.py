import random

class Carte:
    """Classe représentant la carte sous forme de grille N x M."""
    def __init__(self, largeur, hauteur):
        self.largeur = largeur
        self.hauteur = hauteur
        self.grille = [[None for _ in range(hauteur)] for _ in range(largeur)]

    def remplir_carte(self,elements):
        """Remplir la carte avec les objets crées (éléments)"""
                for z in elements:
                    grille[z.x][z.y] = z.type

Utilisation :    
"""on génère les éléments puis on les place sur la carte"""
"""pbm : nb éléments et leur position doivent être aléatoires"""
"""on choisit le mode de commencement (lean, mean, marines) puis le type de répartition (or centré ou non) puis on répartie les ressources de manière aléatoire"""
"""ce qui est aléatoire c'est le type de carte ou (le type de carte et la répartition des ressources sur les cartes)?"""

attrbut statique nb_wood, nb_villageois etc...?

def mode_aleatoire() :
  m=random.randint(1,3)
  if m==1 :
    return "lean"

import Resource 
...

def nb_elements() :
  if mode_aléatoire() == "lean" :
    F=50
    W=200 
    G=50
    T=10
    V=3
  return (F,W,G,T,V)

def type_repartition_aléatoire() :
  m=random.randint(1,2)
  if m==1 :
    return "G_non_centré"

def creation_éléments() : 
  curseur1=1
  curseur2=0
  for i in nb_elements() :
      if curseur1 != 3 :
          x=random.randint(0,200)
          y=random.randint(0,200)
          if curseur1 == 1 :
              for j in range(0,i) :
                  elements[curseur2]=Food(...,x,y)
          else if curseur1 == 2 :
              for j in range(0,i) : 
                  elements[curseur2]=Wood(...,x,y)
      else :
          if type_repartition_aléatoire() == "G_centré" :
              elements[curseur2]=Gold(...,50,50)
      curseur2+=1
      curseur1+=1
  return elements

l_elements=creation_elements()
"""l_elements = [Unit(100, 100, 'guerrier'), Unit(200, 150, 'archer'), Resource('W',20)]"""
carte = Carte(200,200)
carte.remplir_carte(l_elements)

      
