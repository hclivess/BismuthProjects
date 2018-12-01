import sys
sys.path.append("../../Bismuth")

import sqlite3
import time
import classes
import essentials

seed = essentials.keys_load_new()[6] #address
print(seed)

conn = sqlite3.connect("../../Bismuth/static/ledger.db")
conn.text_factory = str
c = conn.cursor()

block = 1

hero = classes.Hero()

#trigger is followed by events affected by modifiers

#define events
events = {seed[0:2] : "heal",
          seed[2:4] : "attack",
          seed[4:6] : "attacked",
          seed[6:8] : "critical_hit"}

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
        enemy = classes.Troll()
    elif event == "goblin":
        enemy = classes.Goblin()
    elif event == "berserker":
        enemy = classes.Berserker()
    elif event == "dragon":
        enemy = classes.Dragon()
    else:
        enemy = None

    return enemy

def attack():
    hero.experience += 1
    damage = hero.power
    enemy.health -= hero.power
    print(f"{enemy.name} suffers {damage} damage and is left with {enemy.health} HP")

def critical_hit():
    hero.experience += 1
    damage = hero.power + hero.experience
    enemy.health -= damage
    print(f"{enemy.name} suffers {damage} critical damage and is left with {enemy.health} HP")

def cycle(block):
    c.execute("SELECT * FROM transactions WHERE block_height = ? ORDER BY block_height", (block,))
    result = c.fetchall()
    block_hash  = result[0][7]
    return block_hash

def heal():
    if hero.in_combat and hero.health < classes.Hero.FULL_HP:
        hero.health = hero.health + 5
        print(f"You drink a potion and heal to {hero.health} HP...")

    elif not hero.in_combat:
        hero.health = 100
        print("You rest and fully heal...")

    if hero.health > classes.Hero.FULL_HP:
        hero.health = classes.Hero.FULL_HP

def attacked():
    hero.in_combat = True
    hero.health = hero.health - enemy.power
    print(f"{enemy.name} hits you for {enemy.power} HP, you now have {hero.health} HP")

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
                            attack()

                        if event == "critical_hit":
                            critical_hit()

                        if event == "heal":
                            heal()

                        if events[event_key] == "attacked":
                            attacked()

                hero_dead_check()
                enemy_dead_check()


                block += 1
                time.sleep(2)


    block += 1



