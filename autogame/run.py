import sqlite3
import core
import classes
import json
import time

db = core.db #do not reinit

while True:
    db.c.execute("SELECT * FROM transactions WHERE operation = ?",("autogame",))
    matches = db.c.fetchall()

    for match in matches:
        core.go(match)

    print ("Run finished, sleeping")
    time.sleep(60)
