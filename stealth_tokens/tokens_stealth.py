import glob
import json
import os
import random
import sqlite3
import string
from hashlib import blake2b
from base64 import b64decode, b64encode
from bismuthclient import bismuthutil

from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes

__version__ = '0.0.1'
connection = sqlite3.connect("D:/bismuth/static/ledger.db")
cursor = connection.cursor()
Bismuthutil = bismuthutil.BismuthUtil()

def blake2b_generate(nonce):
    return blake2b(nonce.encode(), digest_size=20).hexdigest()

def process(nonce):
    if not os.path.exists("stealth_history"):
        os.mkdir("stealth_history")
    hash_path = f'stealth_history/{blake2b_generate(nonce)}'

    if not os.path.exists(hash_path):
        with open(hash_path, "w") as nonce_file:
            nonce_file.write("")

def is_processed(nonce):
    if not os.path.exists("stealth_history"):
        os.mkdir("stealth_history")
    hash_path = f'stealth_history/{blake2b_generate(nonce)}'
    if os.path.exists(hash_path):
        return True
    else:
        return False

def find_txs(signals_dict, anchor):
    signal_set = ','.join('?' for _ in signals_dict)
    query = 'SELECT address, block_height, openfield FROM transactions WHERE operation IN (%s) AND block_height >= %s ORDER BY block_height ASC' % (signal_set, anchor)
    result = cursor.execute(query, signals_dict).fetchall()

    return_list = []
    for entry in result:
        zipped = dict(zip(["address", "block_height", "openfield"], [entry[0], entry[1], json.loads(entry[2])]))
        return_list.append(zipped)

    return return_list


def signals_generate(size):
    signal_list = []
    for item in range(size):
        signal_list.append(''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10)))
    return signal_list


def token_key_generate(len=32):  # AES-256 default
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

    plaintext["name"] = plaintext["name"].lstrip("0")  # remove leading 0s
    plaintext["amount"] = plaintext["amount"].lstrip("0")  # remove leading 0s

    try:
        cipher.verify(b64decode(enc_dict["tag"]))
        return plaintext
    except ValueError:
        print("Key incorrect or message corrupted")


def load_token_dict(token):
    token_path = f'stealth_keys/{token}.json'

    if os.path.exists(token_path):
        with open(token_path) as token_keys:
            keys_loaded = json.loads(token_keys.read())
        return keys_loaded
    else:
        return False


def save_token_key(token, signals, public_signal, key):
    print(public_signal)
    if not os.path.exists("stealth_keys"):
        os.mkdir("stealth_keys")
    token_path = f'stealth_keys/{token}'
    if not os.path.exists(token_path):
        keys = {}
        keys["name"] = token
        keys["key"] = b64encode(key).decode()
        keys["signals"] = signals
        keys["public_signal"] = public_signal[0]

        with open(token_path, "w") as token_keys:
            token_keys.write(json.dumps(keys))


def tokens_update(token_key_dict: dict):
    found_txs = find_txs(signals_dict=token_key_dict["signals"], anchor=0)

    print("Existing transactions for the given master key:")
    for transaction in found_txs:  # print
        try:
            print("transaction", transaction)
            action = decrypt(transaction["openfield"], token_key_dict["key"])
            print(action)

        except Exception as e:
            print(f"Corrupted message: {e}")

    for transaction in found_txs:  # transactions
        try:
            action = decrypt(transaction["openfield"], token_key_dict["key"])

            if not is_processed(transaction["openfield"]["nonce"]):
                process(transaction["openfield"]["nonce"])

                if action["operation"] == "move":
                    account_add_to(account=action["recipient"], token=action["name"], amount=1, debtor=transaction["address"])

                elif action["operation"] == "make":
                    token_genesis(account=action["recipient"], token=action["name"], amount=action["amount"])

            else:
                print("Skipping processed transaction")

        except Exception as e:
            print(f"Corrupted message: {e}")
            raise


def load_signal(signals):
    return random.choice(signals)


def account_file_load(account):
    if not os.path.exists(f"stealth_accounts"):
        os.mkdir(f"stealth_accounts")
    account_path = f"stealth_accounts/{account}.json"

    if not os.path.exists(account_path):
        with open(account_path, "w") as token_keys:
            token_keys.write(json.dumps({}))

    with open(account_path) as file:
        account_contents = json.loads(file.read())

    return account_contents


def account_file_save(account, data):
    account_path = f"stealth_accounts/{account}.json"
    with open(account_path, "w") as account_file:
        account_file.write(json.dumps(data))


def token_genesis(account: str, token: str, amount: int):
    amount = int(amount)
    data = account_file_load(account)
    try:
        data[token]
    except: # if unprocessed
        data[token] = amount
        data["account"] = account

        account_file_save(account, data)


def account_add_to(account: str, token: str, amount: int, debtor: str):
    amount = int(amount)

    if account_take_from(debtor, token, amount):
        data = account_file_load(account)

        try:
            data[token] += amount
        except:
            data[token] = amount

        account_file_save(account, data)


def account_take_from(account: str, token: str, amount: int):
    amount = int(amount)
    data = account_file_load(account)

    try:
        if data[token] - amount >= 0:
            data[token] -= amount
            account_file_save(account, data)
            return True
        else:
            return False
    except:
        print("Insufficient balance or corrupted file")
        return False

def load_tokens():
    token_paths = glob.glob('stealth_keys\*.json')

    token_names = []
    for token_path in token_paths:
        token_names.append(os.path.basename(token_path))

    return token_names


def move_token(token_name: str, recipient: str, amount: str):
    token_key_dict = load_token_dict(token=token_name)
    print("token_key_dict", token_key_dict)

    encrypted_data_move = encrypt_data(token_name=token_name,
                                       token_amount=str(amount),
                                       recipient=recipient,
                                       operation="move",
                                       key_encoded=token_key_dict["key"])

    print(decrypt(encrypted_data_move, token_key_dict["key"]))

    operation = load_signal(token_key_dict["signals"])
    data = json.dumps(encrypted_data_move)
    bisurl = Bismuthutil.create_bis_url(recipient, amount, operation, data)

    print("move (data)", data)
    print("move (operation)", operation)
    print("BISURL to move", bisurl)

    return {"data": data, "operation" : operation, "bisurl": bisurl}

def generate_token(token_name: str, recipient: str, amount: str):
    save_token_key(token=token_name,
                   signals=signals_generate(100),
                   public_signal=signals_generate(1),
                   key=token_key_generate())

    token_key_dict = load_token_dict(token=token_name)
    print("token_key_dict", token_key_dict)

    encrypted_data_make = encrypt_data(token_name=token_name,
                                       token_amount=str(amount),
                                       recipient=recipient,
                                       operation="make",
                                       key_encoded=token_key_dict["key"])


    #print(decrypt(encrypted_data_make, token_key_dict["key"]))

    operation = load_signal(token_key_dict["signals"])
    data = json.dumps(encrypted_data_make)
    bisurl = Bismuthutil.create_bis_url(recipient, amount, operation, data)

    print("make (data)", data)
    print("make (operation)", operation)
    print("BISURL to make", bisurl)

    return {"data": data, "operation" : operation, "bisurl": bisurl}

if __name__ == "__main__":
    # account_add_to(account="test", token="stoken2", amount=1, debtor="test0") #  this is automated based on chain
    # account_add_to(account="test", token="stoken3", amount=1, debtor="test0") #  this is automated based on chain
    # print(account_file_load("test"))

    generate_token(token_name="stest4",
                   recipient="4edadac9093d9326ee4b17f869b14f1a2534f96f9c5d7b48dc9acaed",
                   amount="10000")

    move_token(token_name="stest3",
                recipient="4edadac9093d9326ee4b17f869b14f1a2534f96f9c5d7b48dc9acaed",
                amount="1")

    loaded_tokens = load_tokens()

    for token in loaded_tokens:
        print(token)
        token_key_dict = load_token_dict(token=token)

        tokens_update(token_key_dict)
