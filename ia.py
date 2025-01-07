def building(self, building_type, initial_position) :
             """création building + positionnement sur la map"""
             building = self.place_building(building_type, initial_position)
             """trouver villageois pour le construire"""
             list_villagers = self.allocate_villagers_for_construction(building)
             """construction"""
            start_time = time.time()
             while building.is_under_construction :
                 current_time = time.time()
                 self.reevaluate_construction(building, current_time-start_time,  list_villagers)
                  
        
