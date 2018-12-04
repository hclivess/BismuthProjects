import time
import classes
import sqlite3
import os
import json
from hashlib import blake2b

config = classes.Config()
db = classes.Db(config.path["ledger"])

def go(seed, block):
    game = classes.Game()
    game.start_block = block
    game.block = block
    game.seed = seed
    game.hash = blake2b((seed + str(block)).encode(), digest_size=10).hexdigest()
    game.filename_temp = "static/replays/" + str(game.hash + "_.json")
    game.filename = "static/replays/" + str(game.hash + ".json")

    hero = classes.Hero()


    def output(entry):
        game.step += 1

        print(entry)
        game.story[game.step] = entry

        if game.finished and os.path.exists (game.filename_temp):
            os.remove(game.filename_temp)

            if not os.path.exists (game.filename):
                with open (game.filename, "w") as file:
                    file.write(json.dumps(game.story))

        elif not game.finished:
            with open(game.filename_temp, "w") as file:
                file.write(json.dumps(game.story))

    #trigger is followed by events affected by modifiers

    #define events

    EVENTS = {seed[2:4] : "attack",
              seed[4:6] : "attacked",
              seed[6:8] : "attack_critical"}

    #define triggers
    triggers_combat = {"4f" : "troll",
                       "df" : "goblin",
                       "5a" : "berserker",
                       "61a" : "dragon"
                       }

    triggers_peaceful = {"3d" : "health_potion",
                         "69a": "armor",
                         "70b": "sword"
                         }

    def enemy_dead_check():
        if enemy.health < 1:
            hero.in_combat = False
            enemy.alive = False
            output(f"{enemy.name} died")
            output(f"You now have {hero.experience} experience")

    def hero_dead_check():
        if hero.health < 1:
            hero.alive = False
            game.finished = True
            output(f"You died with {hero.experience} experience")

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

    def sword_get():
        if not hero.inventory["weapon"]:
            hero.inventory["weapon"] = "sword"
            output(f"You obtained a sword")

    def armor_get():
        if not hero.inventory["armor"]:
            hero.inventory["armor"] = "armor"
            output(f"You obtained armor")

    def attack():
        hero.in_combat = True
        hero.experience += 1
        damage = hero.power
        if hero.inventory["weapon"] == "sword":
            damage += 10

        enemy.health -= hero.power
        output(f"{enemy.name} suffers {damage} damage and is left with {enemy.health} HP")
        enemy_dead_check()

    def attack_critical():
        hero.experience += 1
        damage = hero.power + hero.experience
        enemy.health -= damage
        output(f"{enemy.name} suffers {damage} *critical* damage and is left with {enemy.health} HP")
        enemy_dead_check()

    def cycle():
        db.c.execute("SELECT * FROM transactions WHERE block_height = ? ORDER BY block_height", (game.block,))
        result = db.c.fetchall()
        block_hash  = result[0][7]
        return block_hash


    def heal():
        if hero.in_combat:
            hero.health = hero.health + 5
            output(f"You drink a potion and heal to {hero.health} HP...")

        elif not hero.in_combat:
            hero.health = hero.health + 15
            output(f"You rest and heal well to {hero.health} HP...")

        if hero.health > classes.Hero.FULL_HP:
            hero.health = classes.Hero.FULL_HP

    def attacked():
        hero.in_combat = True
        damage_taken = enemy.power

        if hero.inventory["armor"] == "armor":
            damage_taken -= 5

        hero.health = hero.health - damage_taken

        output(f"{enemy.name} hits you for {enemy.power} HP, you now have {hero.health} HP")
        hero_dead_check()

    while hero.alive and not game.quit:

        try:
            block_hash = cycle()
        except:
            output("The game is still running")
            game.quit = True
            break

        for trigger_key in triggers_peaceful:
            trigger = triggers_peaceful[trigger_key]

            if trigger_key in block_hash:
                if trigger == "health_potion" and hero.health < classes.Hero.FULL_HP:
                    heal()
                elif trigger == "armor":
                    armor_get()
                elif trigger == "sword":
                    sword_get()

        for trigger_key in triggers_combat:
            if trigger_key in block_hash and hero.alive:
                trigger = triggers_combat[trigger_key]

                enemy = enemy_define(trigger)
                output(f"You meet {enemy.name} on block {game.block}")

                while hero.alive and enemy.alive and not game.quit:
                    for event_key in EVENTS: #check what happened
                        try:  # roll new hash happen while engaged
                            block_hash = cycle()
                        except:
                            output("The game is still running")
                            game.quit = True
                            break

                        if event_key in block_hash and enemy.alive:
                            event = EVENTS[event_key]
                            output(f"Event: {event}")

                            if event == "attack":
                                attack()

                            elif event == "attack_critical":
                                attack_critical()

                            elif event == "attacked":
                                attacked()

                    game.block += 1
        game.block += 1
    return game,hero



