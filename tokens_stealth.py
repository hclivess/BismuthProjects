# operation: token:issue
# openfield: token_name:total_number(:key)
# - optional key is a hash of password + operation

# operation: token:transfer
# openfield: token_name:amount(:key)
# - optional key is a hash of password + operation

import sqlite3
import log
from hashlib import blake2b

__version__ = '0.0.2'


def blake2bhash_generate(data):
    # new hash
    blake2bhash = blake2b(str(data).encode(), digest_size=20).hexdigest()
    return blake2bhash
    # new hash

def tokens_update(node, db_handler_instance):

    db_handler_instance.index_cursor.execute("CREATE TABLE IF NOT EXISTS tokens (block_height INTEGER, timestamp, token, address, recipient, txid, amount INTEGER)")
    db_handler_instance.index.commit()

    db_handler_instance.index_cursor.execute("SELECT block_height FROM tokens ORDER BY block_height DESC LIMIT 1;")
    try:
        token_last_block = int(db_handler_instance.index_cursor.fetchone()[0])
    except:
        token_last_block = 0

    node.logger.app_log.warning("Token anchor block: {}".format(token_last_block))

    # node.logger.app_log.warning all token issuances
    db_handler_instance.c.execute("SELECT block_height, timestamp, address, recipient, signature, operation, openfield FROM transactions WHERE block_height >= ? AND operation = ? AND reward = 0 ORDER BY block_height ASC;", (token_last_block, "token:issue",))
    token_issuances = db_handler_instance.c.fetchall()
    node.logger.app_log.warning(token_issuances)

    tokens_processed = []

    for issuance in token_issuances:
        try:
            token_split = issuance[6].split(":")
            token_name = token_split[0].lower().strip()

            try:
                token_keyhole = token_split[2]
            except:
                token_keyhole = None

            print(token_name,token_keyhole)


            try:
                db_handler_instance.index_cursor.execute("SELECT * from tokens WHERE token = ?", (token_name,))
                dummy = db_handler_instance.index_cursor.fetchall()[0]  # check for uniqueness
                node.logger.app_log.warning("Token issuance already processed: {}".format(token_name,))
            except:
                if token_name not in tokens_processed:
                    block_height = issuance[0]
                    node.logger.app_log.warning("Block height {}".format(block_height))

                    timestamp = issuance[1]
                    node.logger.app_log.warning("Timestamp {}".format(timestamp))

                    tokens_processed.append(token_name)
                    node.logger.app_log.warning("Token: {}".format(token_name))

                    issued_by = issuance[3]
                    node.logger.app_log.warning("Issued by: {}".format(issued_by))

                    txid = issuance[4][:56]
                    node.logger.app_log.warning("Txid: {}".format(txid))

                    total = issuance[6].split(":")[1]
                    node.logger.app_log.warning("Total amount: {}".format(total))

                    db_handler_instance.index_cursor.execute("INSERT INTO tokens VALUES (?,?,?,?,?,?,?)",
                              (block_height, timestamp, token_name, "issued", issued_by, txid, total))

                    if node.plugin_manager:
                        node.plugin_manager.execute_action_hook('token_issue',
                                                           {'token': token_name, 'issuer': issued_by,
                                                            'txid': txid, 'total': total})

                else:
                    node.logger.app_log.warning("This token is already registered: {}".format(issuance[1]))
        except:
            node.logger.app_log.warning("Error parsing")

    db_handler_instance.index.commit()
    # node.logger.app_log.warning all token issuances

    # node.logger.app_log.warning("---")

    # node.logger.app_log.warning all transfers of a given token
    # token = "worthless"

    db_handler_instance.c.execute("SELECT operation, openfield FROM transactions WHERE (block_height >= ? OR block_height <= ?) AND operation = ? and reward = 0 ORDER BY block_height ASC;",
              (token_last_block, -token_last_block, "token:transfer",)) #includes mirror blocks
    openfield_transfers = db_handler_instance.c.fetchall()
    # print(openfield_transfers)

    tokens_transferred = []
    for transfer in openfield_transfers:
        try:

            token_name = transfer[1].split(":")[0].lower().strip()
            try:
                token_keyhole = transfer[1].split(":")[3].lower().strip()
            except:
                token_keyhole = None

            print(token_name,token_keyhole)

            if token_name not in tokens_transferred:
                tokens_transferred.append(token_name)

        except:
            node.logger.app_log.warning(f"Error parsing")

    if tokens_transferred:
        node.logger.app_log.warning("Token transferred: {}".format(tokens_transferred))

    for token in tokens_transferred:
        node.logger.app_log.warning("processing {}".format(token))
        db_handler_instance.c.execute("SELECT block_height, timestamp, address, recipient, signature, operation, openfield FROM transactions WHERE (block_height >= ? OR block_height <= ?) AND operation = ? AND openfield LIKE ? AND reward = 0 ORDER BY block_height ASC;",
                  (token_last_block, -token_last_block, "token:transfer",token + '%',))
        results2 = db_handler_instance.c.fetchall()
        node.logger.app_log.warning(results2)

        for r in results2:
            block_height = r[0]
            node.logger.app_log.warning("Block height {}".format(block_height))

            timestamp = r[1]
            node.logger.app_log.warning("Timestamp {}".format(timestamp))

            token = r[6].split(":")[0]
            node.logger.app_log.warning("Token {} operation".format(token))

            sender = r[2]
            node.logger.app_log.warning("Transfer from {}".format(sender))

            recipient = r[3]
            node.logger.app_log.warning("Transfer to {}".format(recipient))

            txid = r[4][:56]
            if txid == "0":
                txid = blake2bhash_generate(r)
            node.logger.app_log.warning("Txid: {}".format(txid))

            try:
                transfer_amount = int(r[6].split(":")[1])
            except:
                transfer_amount = 0

            node.logger.app_log.warning("Transfer amount {}".format(transfer_amount))

            # calculate balances
            db_handler_instance.index_cursor.execute("SELECT sum(amount) FROM tokens WHERE recipient = ? AND block_height < ? AND token = ?",
                      (sender,block_height,token,))

            try:
                credit_sender = int(db_handler_instance.index_cursor.fetchone()[0])
            except:
                credit_sender = 0
            node.logger.app_log.warning("Sender's credit {}".format(credit_sender))

            db_handler_instance.index_cursor.execute("SELECT sum(amount) FROM tokens WHERE address = ? AND block_height <= ? AND token = ?",
                      (sender,block_height,token,))
            try:
                debit_sender = int(db_handler_instance.index_cursor.fetchone()[0])
            except:
                debit_sender = 0
            node.logger.app_log.warning("Sender's debit: {}".format(debit_sender))
            # calculate balances

            # node.logger.app_log.warning all token transfers
            balance_sender = credit_sender - debit_sender
            if balance_sender < 0 and sender == "staking":
                node.logger.app_log.warning("Total staked {}".format(abs(balance_sender)))
            else:
                node.logger.app_log.warning("Sender's balance {}".format(balance_sender))
            try:
                db_handler_instance.index_cursor.execute("SELECT txid from tokens WHERE txid = ?", (txid,))
                dummy = db_handler_instance.index_cursor.fetchone()  # check for uniqueness
                if dummy:
                    node.logger.app_log.warning("Token operation already processed: {} {}".format(token, txid))
                else:
                    if (balance_sender - transfer_amount >= 0 and transfer_amount > 0) or (sender == "staking"):
                        db_handler_instance.index_cursor.execute("INSERT INTO tokens VALUES (?,?,?,?,?,?,?)",
                                  (abs(block_height), timestamp, token, sender, recipient, txid, transfer_amount))
                        if node.plugin_manager:
                            node.plugin_manager.execute_action_hook('token_transfer',
                                                               {'token': token, 'from': sender,
                                                                'to': recipient, 'txid': txid, 'amount': transfer_amount})

                    else:  # save block height and txid so that we do not have to process the invalid transactions again
                        node.logger.app_log.warning("Invalid transaction by {}".format(sender))
                        db_handler_instance.index_cursor.execute("INSERT INTO tokens VALUES (?,?,?,?,?,?,?)", (block_height, "", "", "", "", txid, ""))
            except Exception as e:
                node.logger.app_log.warning("Exception {}".format(e))

            node.logger.app_log.warning("Processing of {} finished".format(token))

        db_handler_instance.index.commit()


if __name__ == "__main__":
    from libs import node,logger
    import dbhandler

    node = node.Node()
    node.debug_level = "WARNING"
    node.terminal_output = True

    node.logger = logger.Logger()
    node.logger.app_log = log.log("stealth.log", node.debug_level, node.terminal_output)
    node.logger.app_log.warning("Configuration settings loaded")

    db_handler = dbhandler.DbHandler("static/index_reg.db","static/regmode.db","static/regmode.db", False, None, node.logger, False)
    #index var is automatically overwritten in regmode

    tokens_update(node, db_handler)
    # tokens_update("tokens.db","reindex")