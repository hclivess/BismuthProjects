import sqlite3
import core
import classes

db = core.db #do not reinit

db.c.execute("SELECT * FROM transactions WHERE operation = ?",("autogame",))
result = db.c.fetchall()
print (result)


scores = classes.Scores()

counter = 0
for entry in result:


    seed = entry[2]  # address
    print(seed)
    block = entry[0]
    print(block)

    game,hero = core.go(seed, block)

    game.id = counter
    scores.history[game.id] = {"block" : game.block,
                               "object" : game,
                               "seed" : game.seed,
                               "experience" : hero.experience,
                               "inventory" : hero.inventory,
                               }



    counter += 1

print (scores.history)
