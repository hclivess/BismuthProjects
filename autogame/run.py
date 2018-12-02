import sqlite3
import core
import classes
import json
from hashlib import blake2b

db = core.db #do not reinit
scores_db = classes.ScoreDb()

db.c.execute("SELECT * FROM transactions WHERE operation = ?",("autogame",))
result = db.c.fetchall()
print (result)

for entry in result:


    seed = entry[2]  # address
    print(seed)
    block = entry[0]
    print(block)

    game,hero = core.go(seed, block)

    game.hash = blake2b((game.seed + str(game.block)).encode(), digest_size=10).hexdigest()

    try:
        scores_db.c.execute("SELECT * FROM scores WHERE hash = ?", (game.hash,))
        dummy = scores_db.c.fetchall()[0]
    except:
        scores_db.c.execute("INSERT INTO scores VALUES (?,?,?,?,?)", (game.block,game.hash,game.seed,hero.experience,json.dumps(hero.inventory),))
        scores_db.conn.commit()

    """
    scores.history[game.id] = {"block" : game.block,
                               "object" : game,
                               "seed" : game.seed,
                               "experience" : hero.experience,
                               "inventory" : hero.inventory,
                               }

    scores.xp[(block,seed)] = hero.experience
    """







#for key, value in scores.history.items():
#    print (value["seed"],value["experience"])


