from models.units.villager import Villager
from models.Buildings.town_center import Town_center
from models.map import Map
from models.units.unit import Unit
from models.units.unit import unitStatus
from models.Resources.Tile import *
import random

class Strategy:
    AGGRESSIVE = "aggressive"
    DEFENSIVE = "defensive"
    ECONOMIC = "economic"
    
    def __init__(self, ai_controller, strategy_type=None):
        self.ai_controller = ai_controller
        self.strategy_type = strategy_type
        self.phase = 1
    
    
   