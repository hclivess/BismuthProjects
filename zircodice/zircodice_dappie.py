import sqlite3, base64, options, os

from Cryptodome.Signature import PKCS1_v1_5
from Cryptodome.Hash import SHA
import time
from decimal import *
from random import randint
import essentials
from essentials import fee_calculate

if not os.path.exists("roll.db"):
    print("Roll database does not exist, if you run this on an existing casino, all bets will be re-rolled and payouts processed")
    input("Press any key to continue")

block_anchor = 1425090 #no payouts before this block

def update_payout(signature):
    results_db = sqlite3.connect("games.db")
    results_db.text_factory = str
    r = results_db.cursor()

    print(signature[:56])
    r.execute("UPDATE bets SET paid = ? WHERE signature = ?", (True, signature))
    results_db.commit()
    results_db.close()

def results_db_insert(tx):
    results_db = sqlite3.connect("games.db")
    results_db.text_factory = str
    r = results_db.cursor()

    r.execute("CREATE TABLE IF NOT EXISTS results ("
              "timestamp	NUMERIC,"
              "address	TEXT,"
              "recipient	TEXT,"
              "amount	NUMERIC,"
              "signature	TEXT,"
              "public_key	TEXT,"
              "operation	TEXT,"
              "openfield	TEXT);")
    results_db.commit()

    try:
        r.execute("SELECT * FROM results WHERE signature = ?;", (tx[5],))
        _ = r.fetchone()[0] #already there
        print(f"Transaction already in the result database for {tx[5][:8]}")
    except:
        print(tx)
        r.execute("INSERT INTO results VALUES (?,?,?,?,?,?,?,?)", (tx[0], tx[1], tx[2], tx[3], tx[4], tx[5], tx[6], tx[7]))
        results_db.commit()

        results_db.close()
        print(f"Local database updated with a result transaction for {tx[4][:8]}")
        
def bets_db_insert(tx, rolled, victorious):
    bets_db = sqlite3.connect("games.db")
    bets_db.text_factory = str
    b = bets_db.cursor()

    b.execute("CREATE TABLE IF NOT EXISTS bets ("
              "block_height	INTEGER,"
              "timestamp	NUMERIC,"
              "address	TEXT,"
              "recipient	TEXT,"
              "amount	NUMERIC,"
              "signature	TEXT,"
              "public_key	TEXT,"
              "block_hash	TEXT,"
              "fee	NUMERIC,"
              "reward	NUMERIC,"
              "operation	TEXT,"
              "openfield	TEXT,"
              "rolled	TEXT,"
              "txid TEXT,"
              "victorious BOOLEAN,"
              "paid BOOLEAN,"
              "binder TEXT);")
    bets_db.commit()

    try:
        b.execute("SELECT * FROM bets WHERE signature = ?;", (tx[5],))
        _ = b.fetchone()[0] #already there
        print(f"Transaction already in the bet database for {tx[5][:8]}")
    except:
        b.execute("INSERT INTO bets VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (tx[0], tx[1], tx[2], tx[3], tx[4], tx[5], tx[6], tx[7], tx[8], tx[9], tx[10], tx[11], rolled, tx[5][:56], victorious, False, tx[5][:8]))
        bets_db.commit()

        bets_db.close()
        print(f"Local database updated with a bet transaction for {tx[5][:8]}")

def results_db_add(tx):
    passed = False
    while not passed:
        try:
            results_db_insert(tx)
            passed = True
        except sqlite3.OperationalError as e:
            print("Database locked, retrying")
            time.sleep(1)

def can_be_added_to_bets(signature):
    results_db = sqlite3.connect("games.db")
    results_db.text_factory = str
    r = results_db.cursor()
    r.execute("SELECT * FROM bets WHERE signature = ?", (signature,))
    result = r.fetchall()
    results_db.close()

    if result:
        print(f"{signature[:8]} cannot be added")
        return False
    else:
        print(f"{signature[:8]} can be added")
        return True


def is_eligible(signature):
    results_db = sqlite3.connect("games.db")
    results_db.text_factory = str
    r = results_db.cursor()
    r.execute("SELECT * FROM bets WHERE signature = ? AND paid = 0 AND victorious = 1", (signature,))
    result = r.fetchall()
    results_db.close()

    if result:
        print(f"{signature[:8]} Eligible")
        return True
    else:
        print(f"{signature[:8]} not eligible")
        return False


def bets_db_add(tx, rolled, victorious):
    passed = False
    while not passed:
        try:
            bets_db_insert(tx, rolled, victorious)
            passed = True
        except sqlite3.OperationalError as e:
            print("Database locked, retrying")
            time.sleep(1)
    print(f"Added to bets database: {tx}")

def roll(block_height, txid):
    roll = sqlite3.connect("roll.db")
    roll.text_factory = str
    r = roll.cursor()
    r.execute("CREATE TABLE IF NOT EXISTS transactions (block_height INTEGER, txid, rolled)")
    roll.commit()

    try:
        r.execute("SELECT rolled FROM transactions WHERE txid = ?",(txid,))
        roll_number = r.fetchone()[0]
    except:
        roll_number = (randint(0, 9))
        r.execute("INSERT INTO transactions VALUES (?,?,?)",(block_height, txid, roll_number))

    roll.commit()
    roll.close()
    return roll_number

def percentage(percent, whole):
    return ((Decimal (percent) * Decimal(whole)) / 100)

if __name__ == "__main__":
    key, public_key_readable, private_key_readable, _, _, public_key_hashed, address, _ = essentials.keys_load_new("wallet.der")

    config = options.Get()
    config.read()
    ledger_path = config.ledger_path
    full_ledger = config.full_ledger
    ledger_path = config.ledger_path
    hyper_path = config.hyper_path
    mempool_path = config.mempool_path

    confirmations = 0
    bet_max = 100
    bet_min = 0.1

    if full_ledger == 1:
        conn = sqlite3.connect(ledger_path)
    else:
        conn = sqlite3.connect(hyper_path)
    conn.text_factory = str
    c = conn.cursor()

    while True:
        try:

            c.execute("SELECT * FROM transactions "
                      "WHERE (openfield = ? OR openfield = ?) "
                      "AND recipient = ?"
                      "AND block_height > ? "
                      "AND amount >= ? "
                      "AND amount <= ? "
                      "ORDER BY block_height "
                      "DESC LIMIT 500",

                      ("odd",
                       "even",
                       address,
                       block_anchor,
                       bet_min,
                       bet_max,))

            result_bets = c.fetchall()

        except sqlite3.OperationalError as e:
            print ("Database locked, retrying")
            time.sleep(1)
            pass

        pay_this = []
        del pay_this[:]

        for x in result_bets:
                openfield = str(x[11])
                if openfield == "even":
                    player = [0, 2, 4, 6, 8]
                    bank = [1, 3, 5, 7, 9]
                else: #if odd
                    player = [1, 3, 5, 7, 9]
                    bank = [0, 2, 4, 6, 8]

                bet_amount = float(x[4])
                block_hash = x[7]
                # print block_hash
                tx_signature = x[5]  # unique
                local_id = tx_signature[:8]
                txid = x[5][:56]
                rolled = roll(x[0],txid)
                # print rolled
                if int(rolled) in player:
                    # print "player wins"
                    victorious = True
                    if is_eligible(x[5]):
                        pay_this.append(x)
                    print("Won")

                else:
                    # print "bank wins"
                    victorious = False
                    print("Lost")

                if can_be_added_to_bets(tx_signature):
                    bets_db_add(x, rolled, victorious)

        for y in pay_this:
            recipient = y[2]
            bet_amount = float(y[4])
            tx_signature = y[5]  # unique
            #print y

            # create transactions for missing payouts
            timestamp = '%.2f' % time.time()
            win_amount = Decimal(bet_amount * 2) - percentage(5, bet_amount)
            payout_operation = "zircodice:payout"
            fee = fee_calculate(local_id)
            payout_amount = '%.8f' % float(win_amount-fee)

            #float(0.01 + (float(win_amount) * 0.001) + (float(len(payout_openfield)) / 100000) + (float(payout_keep) / 10))  # 0.1% + 0.01 dust

            payout_transaction = (
                str(timestamp),
                str(address),
                str(recipient),
                str(payout_amount),
                str(payout_operation),
                str(local_id)
                           )  # this is signed

            h = SHA.new(str(payout_transaction).encode("utf-8"))
            signer = PKCS1_v1_5.new(key)
            signature = signer.sign(h)
            signature_enc = base64.b64encode(signature)
            print("Encoded Signature: {}".format(signature_enc.decode()))

            verifier = PKCS1_v1_5.new(key)
            if verifier.verify(h, base64.b64decode(signature_enc)):
                print("Signature OK")

            whole_tx = (
                str(timestamp),
                str(address),
                str(recipient),
                str(payout_amount),
                str(signature_enc.decode("utf-8")),
                str(public_key_hashed.decode("utf-8")),
                payout_operation,
                local_id,
                str(timestamp))

            mempool = sqlite3.connect(mempool_path)
            mempool.text_factory = str
            m = mempool.cursor()

            while True:
                m.execute("INSERT INTO transactions VALUES (?,?,?,?,?,?,?,?,?)",
                          whole_tx)

                mempool.commit()  # Save (commit) the changes
                mempool.close()
                print (f"Mempool updated with a payout transaction for {local_id}")
                passed_mp = True

                results_db_add(whole_tx)
                update_payout(tx_signature)
                break

                    # create transactions for missing payouts
        time.sleep(15)
