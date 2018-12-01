import sqlite3
import time

conn = sqlite3.connect("../../Bismuth/static/ledger.db")
conn.text_factory = str
c = conn.cursor()

block = 1


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

class berserker:
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

hero = Hero()

#trigger is followed by events affected by modifiers

#define events
events = {"9a" : "heal",
          "6c" : "attack",
          "e2" : "attacked",
          "8f" : "critical_hit"}

#define modifiers
modifiers = {"a1c" : "health_belt",
             "082" : "enchanted_sword"}

#define triggers
triggers = {"4f" : "troll",
            "df" : "goblin",
            "5a" : "berserker",
            "61a" : "dragon"
            }

def enemy_dead_check():
    if enemy.health < 1:
        hero.in_combat = False
        enemy.alive = False
        print(f"{enemy.name} died")
        enemy.alive = False

def hero_dead_check():
    if hero.health < 1:
        print(f"You died with {hero.experience} experience")
        hero.alive = False

def enemy_define(event):
    if event == "troll":
        enemy = Troll()
    elif event == "goblin":
        enemy = Goblin()
    elif event == "berserker":
        enemy = berserker()
    elif event == "dragon":
        enemy = Dragon()
    else:
        enemy = None

    return enemy

def cycle(block):
    c.execute("SELECT * FROM transactions WHERE block_height = ? ORDER BY block_height", (block,))
    result = c.fetchall()
    block_hash  = result[0][7]
    return block_hash

while hero.alive:

    block_hash = cycle(block)

    for trigger_key in triggers:

        if trigger_key in block_hash and hero.alive:
            trigger = triggers[trigger_key]
            enemy = enemy_define(trigger)

            print(f"You meet {enemy.name}")
            hero.in_combat = True

            while hero.alive and enemy.alive:
                block_hash = cycle(block)

                for event_key in events:
                    if event_key in block_hash:
                        event = events[event_key]
                        print(f"Event: {event}")

                        if event == "attack":
                            hero.experience += 1
                            damage = hero.power
                            enemy.health -= hero.power
                            print(f"{enemy.name} suffers {damage} damage and is left with {enemy.health} HP")


                        if event == "critical_hit":
                            hero.experience += 1
                            damage = hero.power+hero.experience
                            enemy.health -= damage
                            print(f"{enemy.name} suffers {damage} critical damage and is left with {enemy.health} HP")


                        if event == "heal":
                            if hero.in_combat and hero.health < Hero.FULL_HP:
                                hero.health = hero.health + 5
                                print(f"You drink a potion and heal to {hero.health} HP...")

                            elif not hero.in_combat:
                                hero.health = 100
                                print ("You rest and fully heal...")

                            if hero.health > Hero.FULL_HP:
                                hero.health = Hero.FULL_HP

                            break

                        if events[event_key] == "attacked":
                            hero.in_combat = True
                            hero.health = hero.health - enemy.power
                            print(f"{enemy.name} hits you for {enemy.power} HP, you now have {hero.health} HP")

                hero_dead_check()
                enemy_dead_check()


                block += 1
                time.sleep(2)


    block += 1



