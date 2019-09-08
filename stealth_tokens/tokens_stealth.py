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

def signals_generate(size):
    signal_list = []
    for item in range(size):
        signal_list.append(''.join(random.choice(string.ascii_letters + string.punctuation + string.digits) for _ in range(10)))
    return signal_list

def token_key_generate(len=32): #AES-256 default
    return get_random_bytes(len)

def encrypt_data(token_name, token_amount, operation, key):
    cipher = AES.new(key, AES.MODE_EAX)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(json.dumps({"name": token_name.zfill(10), "amount": token_amount.zfill(10), "operation":operation}).encode())

    return {"nonce": b64encode(nonce).decode(), "ciphertext": b64encode(ciphertext).decode(),"tag": b64encode(tag).decode()}

def decrypt(enc_dict, key):
    cipher = AES.new(key, AES.MODE_EAX, nonce=b64decode(enc_dict["nonce"]))

    plaintext = json.loads(cipher.decrypt(b64decode(enc_dict["ciphertext"])).decode())

    plaintext["name"] = plaintext["name"].lstrip("0") #remove leading 0s
    plaintext["amount"] = plaintext["amount"].lstrip("0") #remove leading 0s

    try:
        cipher.verify(b64decode(enc_dict["tag"]))
        #print("The message is authentic:", plaintext)
        return plaintext
    except ValueError:
        print("Key incorrect or message corrupted")

def load_token_key(token):
    with open('token_keys.json') as token_keys:
        keys_loaded = json.loads(token_keys.read())
    for key, value in keys_loaded.items():
        if key == token:
            return {"token": token, "token key": b64decode(value)}

def save_token_key(token, signals, key):
    if not os.path.exists(f'{token}_keys.json'):
        keys = {}
        keys["keys"] = b64encode(key).decode()
        keys["signals"] = signals

        with open(f'{token}_keys.json',"w") as token_keys:
            token_keys.write(json.dumps(keys))

def address_token_key_generate(token_key, address):
    address_token_key = blake2b(repr((token_key,address)).encode(), digest_size=7).hexdigest()
    return {"address":address, "address token key": address_token_key}

def tokens_update():
    pass


if __name__ == "__main__":

    #stealth tokens
    stealth_token = "stest"
    address = "fa442ebb19292114f4f9d53a72c6b396472c7971b9de598bc9d0b4cd"

    #print("test", token_key_generate())
    save_token_key(token="stest", signals=signals_generate(10), key=token_key_generate())

    token_key_dict = load_token_key(token=stealth_token)
    print("token_key", token_key_dict)

    address_token_key_dict = address_token_key_generate(token_key=token_key_dict["token key"], address=address)
    print("address_token_key", address_token_key_dict)
    # stealth tokens

    #print("stoken:make")
    #print("stest:10000")

    encrypted_data_make = encrypt_data(token_name="stest", token_amount="10000", operation="make", key=token_key_dict["token key"])
    encrypted_data_move = encrypt_data(token_name="stest", token_amount="1", operation="move", key=token_key_dict["token key"])

    print("encrypted_data_make", encrypted_data_make)
    print(decrypt(encrypted_data_make, token_key_dict["token key"]))

    print("encrypted_data_move", encrypted_data_move)
    print(decrypt(encrypted_data_move, token_key_dict["token key"]))

    #index var is automatically overwritten in regmode

    tokens_update()
    # tokens_update("tokens.db","reindex")
