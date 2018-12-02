import sqlite3
import core
import classes

db = core.db #do not reinit

db.c.execute("SELECT * FROM transactions WHERE operation = ?",("autogame",))
result = db.c.fetchall()
print (result)


all = {}
for entry in result:

    game = classes.Game()
    game.seed = entry[2]  # address
    print(game.seed)
    game.block = entry[0]
    print(game.block)

    game.id = (f"{game.block}{game.seed}")
    all[game.id] = game

    core.go(game.seed,game.block)

print (all)