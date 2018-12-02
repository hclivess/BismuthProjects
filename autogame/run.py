import sqlite3
import core
import classes


game = classes.Game()
db = core.db #do not reinit

db.c.execute("SELECT * FROM transactions WHERE operation = ?",("autogame",))
result = db.c.fetchall()
print (result)

for entry in result:
    game.seed = entry[2]  # address
    print(game.seed)
    game.block = entry[0]
    print(game.block)

    core.go(game.seed,game.block)