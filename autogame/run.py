import sqlite3
import core
import classes
import json
import time

db = core.db #do not reinit

block_height = 950000

while True:
    db.c.execute("SELECT * FROM transactions WHERE operation = ? AND block_height >= ?",("autogame",block_height,))
    matches = db.c.fetchall()

    for match in matches:
        core.go(match)

    print ("Run finished, sleeping")
    time.sleep(60)
