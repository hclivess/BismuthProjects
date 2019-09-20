import sqlite3
import random
import os
import string
from hashlib import blake2b
import json
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
from base64 import b64decode, b64encode

__version__ = '0.0.1'
connection = sqlite3.connect("D:/bismuth/static/ledger.db")
cursor = connection.cursor()

def find_txs(signals_dict, anchor):
    qmarks = ','.join('?' for _ in signals_dict)
    query = 'SELECT block_height, openfield FROM transactions WHERE operation IN (%s) AND block_height >= %s' % (qmarks, anchor)
    result = cursor.execute(query, signals_dict).fetchall()
    return result

def signals_generate(size):
    signal_list = []
    for item in range(size):
        signal_list.append(''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10)))
    return signal_list

def token_key_generate(len=32): #AES-256 default
    return get_random_bytes(len)

def encrypt_data(token_name, token_amount, operation, recipient, key_encoded):
    key = b64decode(key_encoded)
    cipher = AES.new(key, AES.MODE_EAX)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(json.dumps({"name": token_name.zfill(10),
                                                            "amount": token_amount.zfill(10),
                                                            "recipient": recipient,
                                                            "operation": operation}).encode())

    return {"nonce": b64encode(nonce).decode(),
            "ciphertext": b64encode(ciphertext).decode(),
            "tag": b64encode(tag).decode()}

def decrypt(enc_dict, key_encoded):
    key = b64decode(key_encoded)

    cipher = AES.new(key, AES.MODE_EAX, nonce=b64decode(enc_dict["nonce"]))

    plaintext = json.loads(cipher.decrypt(b64decode(enc_dict["ciphertext"])).decode())

    plaintext["name"] = plaintext["name"].lstrip("0") #remove leading 0s
    plaintext["amount"] = plaintext["amount"].lstrip("0") #remove leading 0s

    try:
        cipher.verify(b64decode(enc_dict["tag"]))
        return plaintext
    except ValueError:
        print("Key incorrect or message corrupted")

def load_token_dict(token):
    token_path = f'stealth_data/{token}_keys.json'
    if os.path.exists(token_path):
        with open(token_path) as token_keys:
            keys_loaded = json.loads(token_keys.read())
        return keys_loaded
    else:
        return False

def save_token_key(token, signals, key):
    if not os.path.exists("stealth_data"):
        os.mkdir("stealth_data")
    token_path = f'stealth_data/{token}_keys.json'
    if not os.path.exists(token_path):
        keys = {}
        keys["name"] = token
        keys["key"] = b64encode(key).decode()
        keys["signals"] = signals

        with open(token_path,"w") as token_keys:
            token_keys.write(json.dumps(keys))

def tokens_update():
    pass

def load_signal(signals):
    return random.choice(signals)

if __name__ == "__main__":

    token_name = "stest"
    address = "fa442ebb19292114f4f9d53a72c6b396472c7971b9de598bc9d0b4cd"
    recipient = "46fa2d2f7a8ed7221aa292e36e2c0bfdc6e53e0a4bd65e34694dc94b"

    save_token_key(token="stest",
                   signals=signals_generate(100),
                   key=token_key_generate())

    token_key_dict = load_token_dict(token=token_name)
    print("token_key_dict", token_key_dict)

    encrypted_data_make = encrypt_data(token_name="stest",
                                       token_amount="10000",
                                       recipient=recipient,
                                       operation="make",
                                       key_encoded=token_key_dict["key"])
    encrypted_data_move = encrypt_data(token_name="stest",
                                       token_amount="1",
                                       recipient=recipient,
                                       operation="move",
                                       key_encoded=token_key_dict["key"])


    print(decrypt(encrypted_data_make, token_key_dict["key"]))
    print("make (data)", json.dumps(encrypted_data_make))
    print("make (operation)", load_signal(token_key_dict["signals"]))

    print(decrypt(encrypted_data_move, token_key_dict["key"]))
    print("move (data)", json.dumps(encrypted_data_move))
    print("move (operation)", load_signal(token_key_dict["signals"]))

    x = find_txs(token_key_dict["signals"], 0)
    for y in x:
        print("!!!", y[1])
        print(json.loads(y[1]))

        print(decrypt(y[1], token_key_dict["key"]))
