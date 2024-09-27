import time

def direction(posX, posY, dir):
    if (dir == 'W'):
        posY -= 1
    elif (dir == 'E'):
        posY += 1
    elif (dir == 'N'):
        posX -= 1
    else:
        posX += 1
def findway(posX, posY, desX, desY):
    way = []

class People:
    side = -1
    pos = [-1, -1]
    def __init__(self, hp, atk, spd, range, carry):
        self.hp = hp
        self.atk_power = atk
        self.spd = spd
        self.range = range
        self.carry = carry
    def atk(self, other):
        while (other.hp > 0):
            if (self.side != other.side):
                other.hp -= self.atk_power
                if (other.hp < 0):
                    other.hp = 0
                print(other.hp)
            time.sleep(1)
    def dis(self):
            del self
    def goto(self, posX, posY):
        self.pos[0] = posX
        self.pos[1] = posY
    

    
        

class Villagers(People):
    def __init__(self):
        People.__init__(self, 25, 2, 0.8, 1, 0)