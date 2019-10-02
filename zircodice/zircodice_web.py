import sqlite3, time, re, options
from decimal import *
import essentials
from bismuthclient.bismuthcrypto import keys_load_new

import tornado.ioloop
import tornado.web
from random import randint

key, public_key_readable, private_key_readable, _, _, public_key_hashed, address, keyfile = keys_load_new("wallet.der")

config = options.Get()
config.read()
debug_level = config.debug_level
ledger_path = config.ledger_path
full_ledger = config.full_ledger
ledger_path = config.ledger_path
hyper_path = config.hyper_path

block_anchor = 1300000
#1369139

print("Mounting roll database...")
roll_db = sqlite3.connect("roll.db")
roll_db.text_factory = str
roll_cursor = roll_db.cursor()
print("Roll database mounted...")

def percentage_of(part, whole):
    getcontext().prec = 2  # decimal places
    try:
        result = 100 * (Decimal(part) / Decimal(whole))
    except:
        result = 0

    return '%.2f' % result

def oddity_count(roll_cursor):
    roll_cursor.execute("SELECT COUNT(*) FROM transactions WHERE rolled IN (?,?,?,?,?)", (0, 2, 4, 6, 8,))
    sum_even = roll_cursor.fetchone()[0]
    roll_cursor.execute("SELECT COUNT(*) FROM transactions WHERE rolled IN (?,?,?,?,?)", (1, 3, 5, 7, 9,))
    sum_odd = roll_cursor.fetchone()[0]

    return sum_even, sum_odd

def balancesimple(cursor_db,address):

    cursor_db.execute("SELECT sum(amount) FROM transactions WHERE recipient = ?;", (address,))
    credit_ledger = cursor_db.fetchone()[0]
    credit_ledger = 0 if credit_ledger is None else float('%.8f' % credit_ledger)
    credit = float(credit_ledger)

    cursor_db.execute("SELECT sum(fee),sum(reward),sum(amount) FROM transactions WHERE address = ?;", (address,))
    result = cursor_db.fetchall()[0]

    fees = result[0]
    fees = 0 if fees is None else float('%.8f' % fees)

    rewards = result[1]
    rewards = 0 if rewards is None else float('%.8f' % rewards)

    debit_ledger = result[2]
    debit_ledger = 0 if debit_ledger is None else float('%.8f' % debit_ledger)

    balance = float('%.8f' % (float(credit) - float(debit_ledger) - float(fees) + float(rewards)))

    return balance


def roll(block_height, txid, roll_db, roll_cursor):
    roll_cursor.execute("CREATE TABLE IF NOT EXISTS transactions (block_height INTEGER, txid, rolled)")
    roll_db.commit()

    try:
        roll_cursor.execute("SELECT rolled FROM transactions WHERE txid = ?",(txid,))
        roll_number = roll_cursor.fetchone()[0]
    except:
        roll_number = (randint(0, 9))
        roll_cursor.execute("INSERT INTO transactions VALUES (?,?,?)",(block_height, txid, roll_number))

    roll_db.commit()
    return roll_number

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        print("Main object engaged")

        # redraw chart

        while True:
            try:
                print("Mounting database...")
                if full_ledger:
                    conn = sqlite3.connect(ledger_path)
                else:
                    conn = sqlite3.connect(hyper_path)

                c = conn.cursor()
                print("Database mounted...")

                c.execute("SELECT block_height, timestamp FROM transactions WHERE reward != 0 ORDER BY block_height DESC LIMIT 1;")
                result = c.fetchall()
                last_block_height = result[0][0]
                last_timestamp = result[0][1]

                c.execute("SELECT * FROM transactions WHERE (openfield = ? OR openfield = ?) AND recipient = ? AND block_height > ? ORDER BY block_height DESC, timestamp DESC LIMIT 1000;", ("odd", "even", address, block_anchor,))
                result_bets = c.fetchall() # value to transfer

                c.execute('SELECT * FROM transactions WHERE address = ? AND operation = ? AND block_height > ? ORDER BY block_height DESC, timestamp DESC LIMIT 1000;', (address, "zd_payout", block_anchor,))
                result_payouts = c.fetchall()  # value to transfer
                break

            except Exception as e:
                print("Retrying database access, {}".format(e))
                time.sleep(1)

        betting_signatures = []

        wins_total = 0
        losses_total = 0
        wins_amount = 0
        losses_amount = 0

        bet_rows = []

        for x in result_bets:

            amount = x[4]
            openfield = str(x[11])
            betting_signatures.append(x[5]) #sig
            txid = x[5][:56]
            #print openfield

            rolled = roll(x[1], txid, roll_db, roll_cursor)

            if (rolled % 2 == 0) and (openfield == "even"): #if bets even and wins_total
                cell_color = "#cfe0e8"
                icon = "green"
                result = "win"
                wins_total = wins_total + 1
                wins_amount = wins_amount + amount


            elif (rolled % 2 != 0) and (openfield == "odd"): #if bets odd and wins_total
                cell_color = "#cfe0e8"
                icon = "green"
                result = "win"
                wins_total = wins_total + 1
                wins_amount = wins_amount + amount

            else:
                cell_color = "#87bdd8"
                icon = "red"
                result = "loss"
                losses_total = losses_total + 1
                losses_amount = losses_amount + amount

            bet_rows.append({"block_height": x[0],
                                "time": time.strftime("%Y/%m/%d,%H:%M:%S", time.gmtime(float(x[1]))),
                                "player": x[2],
                                "txid": x[5][:56],
                                "rolled": rolled,
                                "amount": x[4],
                                "result": result,
                                "icon": icon,
                                "cell_color": cell_color,
                                })


        payout_rows = []
        for x in result_payouts:
            if x[10] == "zd_payout":
               
                payout_rows.append({"cell_color": "#daebe8",
                                 "block_height": x[0],
                                 "time": time.strftime("%Y/%m/%d,%H:%M:%S", time.gmtime(float(x[1]))),
                                 "player": x[3],
                                 "txid": x[5][:56],
                                 "amount": x[4]
                                })

        minutes_ago = int((time.time() - float(last_timestamp))/60)
        evens_rolled, odds_rolled = oddity_count(roll_cursor)
        win_percentage = percentage_of(wins_total, losses_total)
        loss_percentage = percentage_of(losses_total, wins_total)
        losses_total = wins_total
        wins_total = losses_total

        self.render("web.html",
                    title="ZircoDice",
                    address=address,
                    minutes_ago=minutes_ago,
                    house_balance=balancesimple(c, address),
                    odds_rolled=odds_rolled,
                    evens_rolled=evens_rolled,
                    win_percentage=win_percentage,
                    loss_percentage=loss_percentage,
                    losses_total=losses_total,
                    wins_total=wins_total,
                    
                    payout_rows=payout_rows,
                    wins_amount=wins_amount,
                    losses_amount=losses_amount,
                    bet_rows=bet_rows,
                    )

def make_app():

    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "static"}),
    ])


if __name__ == "__main__":
    app = make_app()
    app.listen(1212)
    print("Server starting...")
    tornado.ioloop.IOLoop.current().start()