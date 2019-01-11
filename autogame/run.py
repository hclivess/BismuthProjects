import sqlite3
import core
import classes
import json
import time

db = core.db #do not reinit

block_height = 550000

while True:

    iterator = 1
    while iterator <= 2:
        print(f"Iterator: {iterator}")
        db.c.execute("SELECT * FROM transactions WHERE operation = ? AND block_height >= ?",("autogame",block_height,))
        matches = db.c.fetchall()

        for match in matches:
            core.go(match, iterator)

        iterator += 1

    print("Runs finished, sleeping")
    time.sleep(60)
