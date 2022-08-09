import base64
import sqlite3
import time
from decimal import *
from random import randint

from Cryptodome.Hash import SHA
from Cryptodome.Signature import PKCS1_v1_5

import bisbasic.essentials as essentials
import bisbasic.options as options
from bisbasic.essentials import fee_calculate

block_anchor = 2864871  # no payouts before this block


def update_payout(signature):
    print(signature[:56])
    g.execute("UPDATE bets SET settled = ? WHERE signature = ?", (True, signature))
    games_db.commit()


def games_db_insert(tx):
    g.execute("CREATE TABLE IF NOT EXISTS results ("
              "timestamp	NUMERIC,"
              "address	TEXT,"
              "recipient	TEXT,"
              "amount	NUMERIC,"
              "signature	TEXT,"
              "public_key	TEXT,"
              "operation	TEXT,"
              "openfield	TEXT);")
    games_db.commit()

    try:
        g.execute("SELECT * FROM results WHERE signature = ?;", (tx[5],))
        _ = g.fetchone()[0]  # already there
        print(f"Transaction already in the result database for {tx[5][:8]}")
    except:
        print(tx)
        g.execute("INSERT INTO results VALUES (?,?,?,?,?,?,?,?)", (tx[0], tx[1], tx[2], tx[3], tx[4], tx[5], tx[6], tx[7]))
        games_db.commit()

        print(f"Local database updated with a result transaction for {tx[4][:8]}")


def bets_db_insert(tx, rolled, victorious):
    g.execute("CREATE TABLE IF NOT EXISTS bets ("
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
              "settled BOOLEAN,"
              "binder TEXT);")
    games_db.commit()

    try:
        g.execute("SELECT * FROM bets WHERE signature = ?;", (tx[5],))
        _ = g.fetchone()[0]  # already there
        print(f"Transaction already in the bet database for {tx[5][:8]}")
    except:
        g.execute("INSERT INTO bets VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (tx[0], tx[1], tx[2], tx[3], tx[4], tx[5], tx[6], tx[7], tx[8], tx[9], tx[10], tx[11], rolled, tx[5][:56], victorious, False, tx[5][:8]))
        games_db.commit()

        print(f"Local database updated with a bet transaction for {tx[5][:8]}")


def games_db_add(tx):
    passed = False
    while not passed:
        try:
            games_db_insert(tx)
            passed = True
        except sqlite3.OperationalError as e:
            print("Database locked, retrying")
            time.sleep(1)


def can_be_added_to_bets(signature):
    g.execute("SELECT * FROM bets WHERE signature = ?", (signature,))
    result = g.fetchall()

    if result:
        print(f"{signature[:8]} cannot be added")
        return False
    else:
        print(f"{signature[:8]} can be added")
        return True


def is_eligible(signature):
    g.execute("SELECT * FROM bets WHERE signature = ? AND settled = 0 AND victorious = 1", (signature,))
    result = g.fetchall()

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


def roll(timestamp, txid):
    g.execute("CREATE TABLE IF NOT EXISTS rolls (timestamp NUMERIC, txid, rolled NUMERIC)")
    games_db.commit()

    try:
        g.execute("SELECT rolled FROM rolls WHERE txid = ?", (txid,))
        roll_number = g.fetchone()[0]
    except:
        roll_number = randint(0, 9)
        g.execute("INSERT INTO rolls VALUES (?,?,?)", (timestamp, txid, roll_number))

    games_db.commit()
    return roll_number


def percentage(percent, whole):
    return ((Decimal(percent) * Decimal(whole)) / 100)


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

    games_db = sqlite3.connect("games.db")
    games_db.text_factory = str
    g = games_db.cursor()

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
            print("Database locked, retrying")
            time.sleep(1)
            pass

        pay_this = []
        del pay_this[:]

        for x in result_bets:
            openfield = str(x[11])
            if openfield == "even":
                player = [0, 2, 4, 6, 8]
                bank = [1, 3, 5, 7, 9]
            else:  # if odd
                player = [1, 3, 5, 7, 9]
                bank = [0, 2, 4, 6, 8]

            bet_amount = float(x[4])
            block_hash = x[7]
            # print block_hash
            tx_signature = x[5]  # unique
            local_id = tx_signature[:8]
            txid = x[5][:56]
            rolled = roll(x[0], txid)
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
            # print y

            # create transactions for missing payouts
            timestamp = '%.2f' % time.time()
            win_amount = Decimal(bet_amount * 2) - percentage(5, bet_amount)
            payout_operation = "zircodice:payout"
            fee = fee_calculate(y[5][:8])
            payout_amount = '%.8f' % float(win_amount - fee)

            # float(0.01 + (float(win_amount) * 0.001) + (float(len(payout_openfield)) / 100000) + (float(payout_keep) / 10))  # 0.1% + 0.01 dust

            payout_transaction = (
                str(timestamp),
                str(address),
                str(recipient),
                str(payout_amount),
                str(payout_operation),
                str(y[5][:8])
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
                y[5][:8],
                str(timestamp))

            mempool = sqlite3.connect(mempool_path)
            mempool.text_factory = str
            m = mempool.cursor()

            while True:
                m.execute("INSERT INTO transactions VALUES (?,?,?,?,?,?,?,?,?)",
                          whole_tx)

                mempool.commit()  # Save (commit) the changes
                mempool.close()
                print(f"Mempool updated with a payout transaction for {y[5][:8]}")
                passed_mp = True

                games_db_add(whole_tx)  # todo: after 24h, check if the tx exists in the ledger. If not, remove this and update settled to 0 in bets db
                update_payout(tx_signature)
                break

                # create transactions for missing payouts
        time.sleep(15)
