"""utilisation des mÃ©thodes dans la classe Joueur (IA)"""

class Batiment :
    def __init__(self, cost, construction_time, hp, size, symbol, pos, state) :
        self.cost = cost
        self.construction_time = construction_time
        self.hp = hp
        self.symbol = symbol
        self.size = size
        self.pos = pos
        
    """bÃ¢timent construit par 1 ou plusieurs villageois"""
    """bÃ¢timent construit par 1 villageois -> nominal_construction_time"""
    """bÃ¢timent construit par pls villageois -> (3 * nominal_construction_time) / (builders_count + 2)"""
    def building(self, delta_time, builders) :
        for builder in builders :
            builder.is_building = True
        self.time_construction = (3 * self.time_construction) / (1+len(builders) + 2)
        print(f"Construction commencÃ©e. Temps de construction rÃ©el : {self.time_construction} secondes.")
        while (self.construction_time > 0) :
            self.construction_time -= delta_time
        print("Construction terminÃ©e du bÃ¢timent")
        """une fois la construction finie, modifier le statut des constructeurs"""
        for builder in builders :
            builder.is_building = False
    """rend inutile les mÃ©thodes start_building() et update_building() de la classe Villager"""
    """on part du principe qu'on a un nb n de constructeurs et qu'ils restent du dÃ©but Ã  la fin de la construction"""

    def destroy(self) :
        self.hp = 0
        
    def damage(self, unit) :
        self.hp -= unit.attack

    def print_building(self) :
        print(self.symbol)

"""peut faire spawn des villageois"""       
class Town_center(Batiment) :
    """pour chaque type d'unitÃ©s, de ressources et de bÃ¢timents, avoir un attribut statique liste ? non, une liste pour chaque classe mÃ¨re batiment et unit"""
    
    def __init__(self, pos) :
        self.population_max = self.population_max +5
        super().__init__(self, 350, 150, 1000, 4, 'T', pos, 'new')

    def add_ressources(type_ressource) :
        """reprendre le diagramme uml tile pour complÃ©ter le constructeur"""
        return ressource(type_ressource...)

    def remove_ressources (self,number,type) : 
        return

    def spawn_v(self) : 
        self.remove_ressources(self,50,'F')
        return villager(50,25,25,1,'v',2,self.pos + (delta_x, delta_y))
    """(cost1,cost2,training_time,hp,speed,symbol,attack,pos)"""

class House(Batiment) :
    def __init__(self, pos) :
        self.population_max = self.population_max +5
        super().__init__(self, 25, 25, 200, 3, 'H', pos, 'new')

"""ProblÃ¨me pour le contenant"""
class Farm(Batiment) :
    cont = 300
    def __init__(self,pos) :
        super().__init__(self, 60, 10, 100, 2, 'F', pos, 'new')
    
class Barracks(Batiment) :
    def __init__(self,pos) :
        super().__init__(self,175,50,500,3,'B',pos,'new')
    def spawn_swordsman(self):
        self.remove_ressources(self,50,'F')
        self.remove_ressources(self,20,'G')
        return swordsman(50,20,20,40,0.9,'s',4,self.pos + (delta_x, delta_y))
    """(cost1,cost2,training_time,hp,speed,symbol,attack,pos)"""

class Stable(Batiment) :
    def __init__(self,pos) :
        super().__init__(self,175,50,500,3,'S',pos,'new')
    def spawn_horseman(self) :
        self.remove_ressources(self,80,'F')
        self.remove_ressources(self,20,'G')
        return horseman(80,20,30,45,1.2,'h',4,self.pos + (delta_x, delta_y))
    """(cost1,cost2,training_time,hp,speed,symbol,attack,pos)"""

class Archery_Range(Batiment) :
    range = 4
    def __init__(self,pos) :
        super().__init__(self,175,50,500,3,'A',pos,'new')
    def spawn_archer(self) :
        self.remove_ressources(self,25,'W')
        self.remove_ressources(self,45,'G')
        return archer(25,45,30,30,1,'a',4,self.pos + (delta_x, delta_y))
    """(cost1,cost2,training_time,hp,speed,symbol,attack,pos)"""

"""ProblÃ¨me pour le contenant"""
class Camp(Batiment) : 
    cont = 0
    def __init__(self,pos) :
        super().__init__(self,100,25,200,2,'C',pos,'new')
    def add_ressources(type_ressource) :
        """reprendre le diagramme uml tile pour complÃ©ter le constructeur"""
        return ressource(type_ressource...)
    def remove_ressources (self,number,type) : 
        return

class Keep(Batiment) :
    gold_cost=125
    range=8
    attack=5
    def __init__(self,pos) :
        super().__init__(self,35,80,800,1,'K',pos,'new')
    
    def fire_arrows(self,unit) :
        unit.hp = unit.hp - self.attack

