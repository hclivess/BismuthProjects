import sqlite3
import core
import classes
import json
import time

db = core.db #do not reinit

while True:
    db.c.execute("SELECT * FROM transactions WHERE operation = ?",("autogame",))
    result = db.c.fetchall()
    print (result)

    for entry in result:

        seed = entry[2]  # address
        block = entry[0]

        game,hero = core.go(seed, block)

    print ("Run finished, sleeping")
    time.sleep(60)
