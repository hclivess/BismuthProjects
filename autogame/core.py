import time
import classes
import sqlite3

db = classes.Db()


def go(seed, block):

    game = classes.Game()
    game.block = block
    game.seed = seed

    hero = classes.Hero()

    #trigger is followed by events affected by modifiers

    #define events

    EVENTS = {seed[2:4] : "attack",
              seed[4:6] : "attacked",
              seed[6:8] : "critical_hit"}

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
            print(f"{enemy.name} died")
            print(f"You now have {hero.experience} experience")

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

    def sword_get():
        if not hero.inventory["weapon"]:
            hero.inventory["weapon"] = "sword"
            print(f"You obtained a sword")

    def armor_get():
        if not hero.inventory["armor"]:
            hero.inventory["armor"] = "armor"
            print(f"You obtained armor")

    def attack():
        hero.in_combat = True
        hero.experience += 1
        damage = hero.power
        if hero.inventory["weapon"] == "sword":
            damage += 10

        enemy.health -= hero.power
        print(f"{enemy.name} suffers {damage} damage and is left with {enemy.health} HP")
        enemy_dead_check()

    def critical_hit():
        hero.experience += 1
        damage = hero.power + hero.experience
        enemy.health -= damage
        print(f"{enemy.name} suffers {damage} *critical* damage and is left with {enemy.health} HP")
        enemy_dead_check()

    def cycle(block):
        db.c.execute("SELECT * FROM transactions WHERE block_height = ? ORDER BY block_height", (block,))
        result = db.c.fetchall()
        block_hash  = result[0][7]
        return block_hash

    def heal():
        if hero.in_combat:
            hero.health = hero.health + 5
            print(f"You drink a potion and heal to {hero.health} HP...")

        elif not hero.in_combat:
            hero.health = hero.health + 15
            print(f"You rest and heal well to {hero.health} HP...")

        if hero.health > classes.Hero.FULL_HP:
            hero.health = classes.Hero.FULL_HP

    def attacked():
        hero.in_combat = True
        damage_taken = enemy.power

        if hero.inventory["armor"] == "armor":
            damage_taken -= 5

        hero.health = hero.health - damage_taken

        print(f"{enemy.name} hits you for {enemy.power} HP, you now have {hero.health} HP")
        hero_dead_check()

    while hero.alive:

        block_hash = cycle(game.block)

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
                print(f"You meet {enemy.name} on block {block}")

                while hero.alive and enemy.alive:
                    for event_key in EVENTS: #check what happened
                        block_hash = cycle(game.block)  # roll new hash happen while engaged

                        if event_key in block_hash and enemy.alive:
                            event = EVENTS[event_key]
                            print(f"Event: {event}")

                            if event == "attack":
                                attack()

                            elif event == "critical_hit":
                                critical_hit()

                            elif event == "attacked":
                                attacked()

                    game.block += 1
                    time.sleep(2)


        game.block += 1




