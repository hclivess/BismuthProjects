class Hero:
    FULL_HP = 500

    def __init__(self):
        self.health = self.FULL_HP
        self.power = 10
        self.alive = True
        self.in_combat = False
        self.experience = 0

class Troll:
    def __init__(self):
        self.name = "Troll"
        self.health = 20
        self.power = 15
        self.alive = True

class Goblin:
    def __init__(self):
        self.name = "Goblin"
        self.health = 10
        self.power = 10
        self.alive = True

class Berserker:
    def __init__(self):
        self.name = "Berserker"
        self.health = 5
        self.power = 30
        self.alive = True

class Dragon:
    def __init__(self):
        self.name = "Dragon"
        self.health = 30
        self.power = 50
        self.alive = True