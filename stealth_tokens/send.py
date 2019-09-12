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
import json

from Cryptodome.Hash import SHA
from Cryptodome.Signature import PKCS1_v1_5

from bisbasic import essentials, options
from bismuthclient import rpcconnections
from bisbasic.essentials import fee_calculate
from polysign.signerfactory import SignerFactory
import tokens_stealth

class TokenTransaction():
    def __init__(self):
        self.operation_input = None
        self.openfield_input = None
        self.recipient_input = None
        self.amount_input = 0
        self.request_confirmation = None
        self.wallet_file = "wallet.der"
        self.token_key_dict = None
        self.token_amount_input = "0"

def send_tx(s, tx_submit):
    while True:
        try:
            s._send("mpinsert")
            s._send(tx_submit)
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
            tx_submit = (str(transaction.timestamp),
                         str(address),
                         str(transaction.recipient_input),
                         '%.8f' % float(transaction.amount_input),
                         str(signature_enc.decode("utf-8")),
                         str(public_key_b64encoded.decode("utf-8")),
                         str(transaction.operation_input),
                         str(transaction.openfield_input))

            return tx_submit
    else:
        print("Invalid signature")

    if not SignerFactory.address_is_valid(transaction.recipient_input):
        print("Wrong address format")
        sys.exit(1)

def connect(ip):
    if 'regnet' in config.version:
        port = 3030
    elif 'testnet' in config.version:
        port = 2829
    else:
        port = 5658

    return rpcconnections.Connection((ip, int(port)))

if __name__ == "__main__":
    config = options.Get()
    config.read()
    transaction = TokenTransaction()

    s = connect("127.0.0.1")

    key, public_key_readable, private_key_readable, encrypted, unlocked, public_key_b64encoded, address, keyfile = essentials.keys_load_new(transaction.wallet_file)

    if encrypted:
        key, private_key_readable = essentials.keys_unlock(private_key_readable)

    print(f'Using address: {address}')

    ### generate
    generate = input("Generate new token? (y/n)")
    if generate == "y":
        generate_name = input("Token name to generate: ")
        tokens_stealth.save_token_key(token=generate_name,
                                      signals=tokens_stealth.signals_generate(100),
                                      key=tokens_stealth.token_key_generate())

        print(f"Master file for {generate_name} generated")

        transaction.token_key_dict = tokens_stealth.load_token_dict(token=generate_name)
        transaction.token_amount_input = input("Amount to generate: ")
        transaction.openfield_input = tokens_stealth.encrypt_data(token_name=generate_name,
                                                                  token_amount=transaction.token_amount_input,
                                                                  recipient=address, operation="make",
                                                                  key_encoded=transaction.token_key_dict["key"])
        transaction.operation_input = tokens_stealth.load_signal(transaction.token_key_dict["signals"])
    ### /generate

    ### load
    else:
        input_name = input("Token name to load: ")
        transaction.token_key_dict = tokens_stealth.load_token_dict(token=input_name)
        transaction.token_amount_input = input("Amount to transfer: ")
        transaction.openfield_input = tokens_stealth.encrypt_data(token_name=input_name,
                                                                  token_amount=transaction.token_amount_input,
                                                                  recipient=address, operation="move",
                                                                  key_encoded=transaction.token_key_dict["key"])
    ### /load

    # get balance

    s._send ("balanceget")
    s._send (address)  # change address here to view other people's transactions
    stats_account = s._receive()
    balance = stats_account[0]

    print(f"Transaction address: ")
    print(f"Transaction address balance: {balance}")

    fee = fee_calculate(transaction.openfield_input)
    print(f"Fee: {fee}")

    if transaction.request_confirmation:
        confirm = input("Confirm (y/n): ")

        if confirm != 'y':
            print("Transaction cancelled, user confirmation failed")
            exit(1)

    tx_submit = verify()
    send_tx(s, tx_submit)

    s.close()
