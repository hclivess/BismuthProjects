import sqlite3
import core
import classes
import json

db = core.db #do not reinit
scores_db = classes.ScoreDb()

db.c.execute("SELECT * FROM transactions WHERE operation = ?",("autogame",))
result = db.c.fetchall()
print (result)

for entry in result:

    seed = entry[2]  # address
    block = entry[0]

    game,hero = core.go(seed, block)

    if game.finished:

        try:
            scores_db.c.execute("SELECT * FROM scores WHERE hash = ?", (game.hash,))
            dummy = scores_db.c.fetchall()[0]
        except:
            scores_db.c.execute("INSERT INTO scores VALUES (?,?,?,?,?)", (game.block,game.hash,game.seed,hero.experience,json.dumps(hero.inventory),))
            scores_db.conn.commit()

