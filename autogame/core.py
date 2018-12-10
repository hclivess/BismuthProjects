import time
import classes
import sqlite3
import os
import json
from hashlib import blake2b

coordinator = "fefb575972cd8fdb086e2300b51f727bb0cbfc33282f1542e19a8f1d"
league_requirement = 5

config = classes.Config()
db = classes.Db(config.path["ledger"])
scores_db = classes.ScoreDb()

def go(match):

    game = classes.Game()
    game.properties = {"seed":match[2],"block":match[0],"recipient":match[3],"amount" : match[4], "league" : match[11]}

    game.start_block = game.properties["block"]
    game.recipient = game.properties["recipient"]
    game.bet = game.properties["amount"]
    game.current_block = game.start_block
    game.seed = game.properties["seed"]
    game.hash = blake2b((game.properties["seed"] + str(game.properties["block"])).encode(), digest_size=10).hexdigest()

    if game.recipient == coordinator and game.bet >= league_requirement:
        game.league = game.properties["league"]
    else:
        game.league = "casual"


    game.filename_temp = "static/replays/unfinished/" + str(game.hash + ".json")
    game.filename = "static/replays/" + str(game.hash + ".json")


    def db_output():

        if not game.finished:
            scores_db.c.execute("DELETE FROM unfinished WHERE hash = ?", (game.hash,))  # remove temp entry if exists
            scores_db.c.execute("INSERT INTO unfinished VALUES (?,?,?,?,?,?,?)",(game.properties["block"], game.hash, game.seed, hero.experience, json.dumps(hero.inventory),game.league,game.bet,))
            scores_db.conn.commit()

        elif game.finished and not game.replay_exists:
            scores_db.c.execute("DELETE FROM unfinished WHERE hash = ?", (game.hash,))  # remove temp entry if exists
            scores_db.c.execute("INSERT INTO scores VALUES (?,?,?,?,?,?,?)", (game.properties["block"], game.hash, game.seed, hero.experience, json.dumps(hero.inventory),game.league,game.bet,))
            scores_db.conn.commit()             


    def output(entry):
        game.step += 1
        print(entry)
        game.story[game.step] = entry

    def replay_save():

        if not os.path.exists("static"):
            os.mkdir("static")
        if not os.path.exists("static/replays"):
            os.mkdir("static/replays")
        if not os.path.exists("static/replays/unfinished"):
            os.mkdir("static/replays/unfinished")


        if game.finished and not game.replay_exists:
            if os.path.exists (game.filename_temp):
                os.remove(game.filename_temp)
            with open (game.filename, "w") as file:
                file.write(json.dumps(game.story))

        elif not game.finished:
            with open(game.filename_temp, "w") as file:
                file.write(json.dumps(game.story))

    if os.path.exists(game.filename):
        game.finished = True
        game.quit = True
        game.replay_exists = True
        output(f"Replay for {game.hash} already present, skipping match")


    hero = classes.Hero()

    #trigger is followed by events affected by modifiers

    #define events

    EVENTS = {game.properties["seed"][2:4] : "attack",
              game.properties["seed"][4:6] : "attacked",
              game.properties["seed"][6:8] : "attack_critical"}

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

    triggers_human_individual = {"item:chaos_ring" : "chaos_ring"}
    triggers_human_global = {"event:rangarok" : "ragnarok"}

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
        elif event == "fenrir": #only triggers on ragnarok
            enemy = classes.Fenrir()
        elif event == "dwarf": #only triggers on ragnarok
            enemy = classes.Dwarf()
        else:
            enemy = None

        return enemy

    def chaos_ring():
        if not hero.inventory["ring"]:
            output(f'You see a chaos ring, the engraving says {subcycle["cycle_hash"][0:5]}')
            if subcycle["cycle_hash"][0] in ["0","1","2","3","4","5","6","7","8","9"]:
                hero.inventory["ring"] = "ring_perseverance"
                hero.full_hp = 650
                if hero.health < hero.full_hp:
                    hero.health = hero.full_hp

                output(f"You slide the ring on your finger and immediately feel stronger")
            else:
                hero.inventory["ring"] = "ring_blight"
                hero.full_hp = 350
                if hero.health > hero.full_hp:
                    hero.health = hero.full_hp
                output(f"You slide the ring on your finger and your hands start to tremble")


    def ragnarok():
        output(f"Ragnarök begins")
        # add new monsters to the world
        triggers_combat["53b"] = "fenrir"
        triggers_combat["4c"] = "dwarf"

    def sword_get():
        if not hero.inventory["weapon"]:
            hero.inventory["weapon"] = "sword"
            output(f"You obtained a sword")

    def armor_get():
        if not hero.inventory["armor"]:
            hero.inventory["armor"] = "armor"
            output(f"You obtained armor")

    def attack():
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
        db.c.execute("SELECT * FROM transactions WHERE block_height = ? ORDER BY block_height", (game.current_block,))
        result = db.c.fetchall()

        position = 0
        game.cycle = {} #remove previous cycle if exists
        for tx in result:
            position = position + 1

            block_height = tx[0]
            timestamp = tx[1]
            address = tx[2]
            recipient = tx[3]
            amount = tx[4]
            block_hash  = tx[7]
            operation = tx[10]
            data = tx[11]

            cycle_hash = blake2b((str(tx)).encode(), digest_size=60).hexdigest()

            game.cycle[position] = {"block_height":block_height,"timestamp":timestamp,"address":address,"recipient":recipient,":amount":amount,"block_hash":block_hash,"operation":operation,"data":data, "cycle_hash":cycle_hash}

    def heal():
        if hero.in_combat:
            hero.health = hero.health + 5
            output(f"You drink a potion and heal to {hero.health} HP...")
            if hero.health > hero.full_hp:
                hero.health = hero.full_hp

        elif not hero.in_combat:
            hero.health = hero.health + 15
            if hero.health > hero.full_hp:
                hero.health = hero.full_hp
            output(f"You rest and heal well to {hero.health} HP...")



    def attacked():
        damage_taken = enemy.power

        if hero.inventory["armor"] == "armor":
            damage_taken -= 5

        hero.health = hero.health - damage_taken

        output(f"{enemy.name} hits you for {enemy.power} HP, you now have {hero.health} HP")
        hero_dead_check()






    while hero.alive and not game.quit:

        cycle()
        if not game.cycle:
            output("The game is still running")
            game.quit = True
            break

        for subposition, subcycle in game.cycle.items(): #for tx in block
            print (subcycle)

            # human interaction
            for trigger_key in triggers_human_individual:
                trigger = triggers_human_individual[trigger_key]
                if trigger_key == subcycle["data"] and subcycle["address"] == game.seed and subcycle["operation"] == "autogame:add":
                    if trigger == "chaos_ring":
                        chaos_ring()

            for trigger_key in triggers_human_global:
                trigger = triggers_human_global[trigger_key]
                if trigger_key == subcycle["data"] and subcycle["operation"] == "autogame:add":
                    if trigger == "ragnarok":
                        ragnarok()
            # human interaction


            for trigger_key in triggers_peaceful:
                if not hero.in_combat:
                    trigger = triggers_peaceful[trigger_key]

                    if trigger_key in subcycle["cycle_hash"]:
                        if trigger == "health_potion" and hero.health < hero.full_hp:
                            heal()
                        elif trigger == "armor":
                            armor_get()
                        elif trigger == "sword":
                            sword_get()

            for trigger_key in triggers_combat:
                if trigger_key in subcycle["cycle_hash"] and hero.alive and not hero.in_combat:
                    trigger = triggers_combat[trigger_key]

                    enemy = enemy_define(trigger)
                    output(f"You meet {enemy.name} on transaction {subposition} of block {game.current_block}")
                    hero.in_combat = True



            for event_key in EVENTS: #check what happened
                if hero.in_combat and hero.alive and not game.quit:

                    if event_key in subcycle["cycle_hash"] and enemy.alive:
                        event = EVENTS[event_key]
                        output(f"Event: {event}")

                        if event == "attack":
                            attack()

                        elif event == "attack_critical":
                            attack_critical()

                        elif event == "attacked":
                            attacked()

        game.current_block = game.current_block + 1

    replay_save()
    db_output()

    return game,hero



