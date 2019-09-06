"""
Send a transaction from console, with no password nor confirmation asked.
To be used for unattended, automated processes.

This file takes optional arguments,

arg1: amount to send
arg2: recipient address
arg3: operation
arg4: OpenField data
arg5: wallet file
arg6: request confirmation for every transaction

args3,4,6 are not prompted if ran without args
"""

import base64
import sys
import time

from Cryptodome.Hash import SHA
from Cryptodome.Signature import PKCS1_v1_5

from bisbasic import essentials, options
from bismuthclient import rpcconnections
from bisbasic.essentials import fee_calculate
from polysign.signerfactory import SignerFactory

class TokenTransaction():
    def __init__(self):
        self.operation_input = ""
        self.openfield_input = ""
        self.recipient_input = ""
        self.amount_input = ""
        self.request_confirmation = ""
        self.wallet_file = ""
        self.tx_submit = None

def send_tx():
    while True:
        try:
            s._send("mpinsert")
            s._send(transaction.tx_submit)
            reply = s._receive()
            print("Client: {}".format(reply))
            if reply != "*":  # response can be empty due to different timeout setting
                break
            else:
                print("Connection cut, retrying")

        except Exception as e:
            print(f"A problem occurred: {e}, retrying")
            pass

def verify():
    transaction.timestamp = '%.2f' % (time.time() - 5)  # remote proofing
    # TODO: use transaction object, no dup code for buffer assembling
    tx = (str(transaction.timestamp),
          str(address),
          str(transaction.recipient_input),
          '%.8f' % float(transaction.amount_input),
          str(transaction.operation_input),
          str(transaction.openfield_input))  # this is signed

    # TODO: use polysign here
    h = SHA.new(str(tx).encode("utf-8"))
    signer = PKCS1_v1_5.new(key)
    signature = signer.sign(h)
    signature_enc = base64.b64encode(signature)
    txid = signature_enc[:56]

    print(f"Encoded Signature: {signature_enc.decode('utf-8')}")
    print(f"Transaction ID: {txid.decode('utf-8')}")

    verifier = PKCS1_v1_5.new(key)

    if verifier.verify(h, signature):
        if float(transaction.amount_input) < 0:
            print("Signature OK, but cannot use negative amounts")

        elif float(transaction.amount_input) + float(fee) > float(balance):
            print("Mempool: Sending more than owned")

        else:
            transaction.tx_submit = (str(transaction.timestamp),
                         str(address),
                         str(transaction.recipient_input),
                         '%.8f' % float(transaction.amount_input),
                         str(signature_enc.decode("utf-8")),
                         str(public_key_b64encoded.decode("utf-8")),
                         str(transaction.operation_input),
                         str(transaction.openfield_input))
    else:
        print("Invalid signature")

def connect(ip):
    if 'regnet' in config.version:
        port = 3030
    elif 'testnet' in config.version:
        port = 2829
    else:
        port = 5658

    return rpcconnections.Connection((ip, int(port)))

def getargs():
    try:
        transaction.wallet_file = sys.argv[5]
    except:
        transaction.wallet_file = input("Path to wallet: ")

    try:
        transaction.request_confirmation = sys.argv[6]
    except:
        transaction.request_confirmation = False

    try:
        transaction.amount_input = sys.argv[1]
    except IndexError:
        transaction.amount_input = input("Amount: ")

    try:
        transaction.recipient_input = sys.argv[2]
    except IndexError:
        transaction.recipient_input = input("Recipient: ")

    if not SignerFactory.address_is_valid(transaction.recipient_input):
        print("Wrong address format")
        sys.exit(1)

    try:
        transaction.operation_input = sys.argv[3]
    except IndexError:
        transaction.operation_input = ""

    try:
        transaction.openfield_input = sys.argv[4]
    except IndexError:
        transaction.openfield_input = ""


if __name__ == "__main__":
    config = options.Get()
    config.read()
    transaction = TokenTransaction()

    s = connect("127.0.0.1")



    key, public_key_readable, private_key_readable, encrypted, unlocked, public_key_b64encoded, address, keyfile = essentials.keys_load_new(transaction.wallet_file)

    if encrypted:
        key, private_key_readable = essentials.keys_unlock(private_key_readable)

    print(f'Number of arguments: {len(sys.argv)} arguments.')
    print(f'Argument list: {"".join(sys.argv)}')
    print(f'Using address: {address}')

    # get balance

    s._send ("balanceget")
    s._send (address)  # change address here to view other people's transactions
    stats_account = s._receive()
    balance = stats_account[0]

    print("Transaction address: %s" % address)
    print("Transaction address balance: %s" % balance)

    getargs()

    fee = fee_calculate(transaction.openfield_input)
    print("Fee: %s" % fee)

    if transaction.request_confirmation:
        confirm = input("Confirm (y/n): ")

        if confirm != 'y':
            print("Transaction cancelled, user confirmation failed")
            exit(1)

    try:
        float(transaction.amount_input)
        is_float = 1
    except ValueError:
        is_float = 0
        sys.exit(1)

    verify()
    send_tx()

    s.close()
