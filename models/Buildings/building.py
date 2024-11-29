"""utilisation des mÃ©thodes dans la classe Joueur (IA)"""

class Building :
    def __init__(self, cost, construction_time, hp, size, symbol, pos) :
        self.cost = cost
        self.construction_time = construction_time
        self.hp = hp
        self.symbol = symbol
        self.size = size
        self.pos = pos
        #self.state = state
        
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

