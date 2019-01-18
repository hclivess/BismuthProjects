import sqlite3
import core
import classes
import json
import time

db = core.db #do not reinit

block_height = 1000110
coordinator = "fefb575972cd8fdb086e2300b51f727bb0cbfc33282f1542e19a8f1d"
league_requirement = 0

while True:

    iterator = 1
    while iterator <= 2:
        print(f"Iterator: {iterator}")
        db.c.execute("SELECT * FROM transactions WHERE operation = ? AND block_height >= ?",("autogame",block_height,))
        matches = db.c.fetchall()

        for match in matches:
            core.go(match, iterator, coordinator, league_requirement)

        iterator += 1

    print("Runs finished, sleeping")
    time.sleep(60)
