#generates a text file with last 50 txs

import sqlite3
import json

class DbHandler():
    def __init__(self):
        self.database = sqlite3.connect("static/ledger.db")
        self.database.text_factory = str
        self.cursor = self.database.cursor()

db_handler = DbHandler()

db_handler.cursor.execute("SELECT * FROM transactions ORDER BY block_height DESC LIMIT 50")
transactions = db_handler.cursor.fetchall()

db_handler.cursor.execute("SELECT * FROM misc ORDER BY block_height DESC LIMIT 50")
misc = db_handler.cursor.fetchall()

with open("last50blocks.txt", "w+") as outfile:
    outfile.write(json.dumps(transactions))
    outfile.write(json.dumps(misc))