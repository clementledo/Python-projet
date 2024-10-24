import time


class Building:
    def __init__(self, x, y, building_type, health, cost, owner, map, size=(1, 1),):

        self.x = x  # X position on the map (top-left corner)
        self.y = y  # Y position on the map (top-left corner)
        self.position = (x, y)
        self.building_type = building_type  # Type of building
        self.max_health = health  # Maximum health of the building
        self.health = 0  # Initial health is 0 since it starts unbuilt
        self.cost = cost  # Resource cost to build the building
        self.owner = owner  # Owner of the building (AI or player)
        self.size = size  # Size of the building (width, height)
        self.is_under_construction = True  # Indicates if the building is being constructed
        self.construction_start_time = None  # Time when construction started
        self.build_time = 0  # Time required to build the building
        self.map = map

    def start_construction(self, build_time): #Faut changer
        """
        Begin the construction of the building.
        
        :param build_time: Time in seconds required to build the building.
        """
        self.build_time = build_time
        self.construction_start_time = time.time()  # Log the current time
        self.is_under_construction = True
        print(f"Construction of {self.building_type} started. It will take {build_time} seconds.")

    def check_construction(self):
        """
        Check if the building is finished constructing. Update health to max if done.
        """
        if self.is_under_construction:
            elapsed_time = time.time() - self.construction_start_time
            if elapsed_time >= self.build_time:
                self.health = self.max_health  # Fully constructed
                self.is_under_construction = False
                print(f"{self.building_type} is fully constructed!")
                self.map.place_building(self)

    def is_alive(self):
        return self.health > 0

    def take_damage(self, damage):
        if not self.is_under_construction:  # Only apply damage if fully constructed
            self.health -= damage
            if self.health <= 0:
                self.destroy()

    def destroy(self):
        print(f"The {self.building_type} at ({self.x}, {self.y}) has been destroyed.")
        self.map.remove_building(self)
