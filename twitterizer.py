# add additional info to the tweet: address that is allowed to withdraw
sleep_interval = 900
payout_level = 1
payout_gap = 4
month = 2629743
lookback = 20
exposure = 5
anchor = 1000000

import json
import os
import re
import sqlite3
import time

import socks
import tweepy

import connections
import essentials
import options

config = options.Get()
config.read()
debug_level = config.debug_level
ledger_path = config.ledger_path
full_ledger = config.full_ledger
hyper_path = config.hyper_path
terminal_output = config.terminal_output
version = config.version

file = open('secret.json', 'r').read()
parsed = json.loads(file)
consumer_key = parsed['consumer_key']
consumer_secret = parsed['consumer_secret']
access_token = parsed['access_token']
access_token_secret = parsed['access_token_secret']
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

#key, public_key_readable, private_key_readable, encrypted, unlocked, public_key_hashed, myaddress, keyfile = essentials.keys_load()
key, public_key_readable, private_key_readable, _, _, public_key_hashed, myaddress, _ = essentials.keys_load("wallet.der")


def is_already_paid(tweet):
    try:
        t.execute("SELECT * FROM tweets WHERE tweet = ?", (tweet,))
        dummy = t.fetchone()[0]
        already_paid = True
    except:
        already_paid = False

    print("already_paid", already_paid)
    return already_paid
   
    
def tweet_parse(tweet_id):
    try:
        open_status = api.get_status(tweet_id, tweet_mode="extended")
        parsed = open_status._json

        parsed_id = parsed['user']['id']  # add this
        favorite_count = parsed['favorite_count']
        retweet_count = parsed['retweet_count']
        parsed_text = parsed['full_text']
        parsed_followers = parsed['user']['followers_count']
        acc_age = time.mktime(time.strptime(parsed['user']['created_at'], '%a %b %d %H:%M:%S +0000 %Y'))

        # if "#bismuth" and "$bis" in parsed_text.lower() and retweet_count + favorite_count > exposure and parsed_followers > 30 and acc_age < time.time() - month:
        if "#bismuth" and "$bis" in parsed_text.lower() and retweet_count + favorite_count > exposure:  # condition
            qualifies = True
        else:
            qualifies = False

        print("parsed_id",
              parsed_id,
              "favorite_count",
              favorite_count,
              "retweet_count",
              retweet_count,
              "parsed_text",
              parsed_text,
              "parsed_followers",
              parsed_followers,
              "acc_age",
              acc_age,
              "qualifies",
              qualifies)

    except Exception as e:
        print(f"Exception with {tweet_id}: {e}")
        qualifies, parsed_text, parsed_id = False, False, False

    return {"qualifies": qualifies, "parsed_text": parsed_text, "parsed_id": parsed_id}


def process_tweet_id(data):
    try:
        if data.isdigit():
            return data
        else:
            processed = re.findall("(\d+){8,}", data)
            return processed[0]
    except:
        print(f"Unable to process {data}")

def define_databases():
    if not os.path.exists('twitter.db'):
        # create empty mempool
        twitter = sqlite3.connect('twitter.db')
        twitter.text_factory = str
        t = twitter.cursor()
        t.execute("CREATE TABLE IF NOT EXISTS tweets ("
                  "block_height,"
                  "address,"
                  "openfield,"
                  "tweet,"
                  "user)")
        twitter.commit()
        print("Created twitter database")
    else:
        twitter = sqlite3.connect('twitter.db')
        twitter.text_factory = str
        t = twitter.cursor()
        print("Connected twitter database")

    # ledger
    if full_ledger == 1:
        conn = sqlite3.connect(ledger_path)
    else:
        conn = sqlite3.connect(hyper_path)
    conn.text_factory = str
    c = conn.cursor()
    # ledger


    return twitter, t, conn, c

if __name__ == "__main__":
    twitter, t, conn, c = define_databases()

    while True:
        # twitter limits: 180 requests per 15m
        for row in c.execute("SELECT * FROM "
                             "(SELECT block_height, address, openfield FROM transactions WHERE operation = ? ORDER BY block_height DESC LIMIT ?) "
                             "ORDER BY block_height ASC", ("twitter", lookback)):  # select top *, but order them ascendingly so older have priority


            tweet_id = process_tweet_id(row[2])
            tweet_parsed = tweet_parse(tweet_id)
            name = tweet_parsed["parsed_id"]

            t.execute("SELECT COUNT() FROM (SELECT * FROM tweets ORDER BY block_height DESC LIMIT ?) WHERE name = ?", (payout_gap, name,))
            name_count = t.fetchone()[0]

            print("name_count", name_count)

            if tweet_parsed["qualifies"] and not is_already_paid(tweet_parsed["parsed_text"]):
                print("Tweet qualifies")

                recipient = row[1]
                amount = payout_level
                operation = "twitter:payout"
                openfield = ""

                timestamp = '%.2f' % time.time()
                tx_submit = essentials.sign_rsa(timestamp, myaddress, recipient, amount, operation, openfield, key, public_key_hashed)

                if tx_submit:
                    s = socks.socksocket()
                    s.settimeout(0.3)
                    print(tx_submit)

                    s.connect(("127.0.0.1", int(5658)))
                    print("Status: Connected to node")
                    while True:
                        connections.send(s, "mpinsert", 10)
                        connections.send(s, tx_submit, 10)
                        reply = connections.receive(s, 10)
                        print(f"Payout result: {reply}")
                        break

                    if reply[-1] == "Success":
                        t.execute("INSERT INTO tweets VALUES (?, ?, ?, ?, ?)", (row[0],
                                                                                row[1],
                                                                                row[2],
                                                                                tweet_parsed["parsed_text"],
                                                                                name))
                        twitter.commit()
                        print("Tweet saved to database")

                        try:
                            api.retweet(tweet_id)
                        except Exception as e:
                            print(e)

                        try:
                            api.update_status("Bismuth address {recipient} wins a giveaway of {amount} $BIS for https://twitter.com/web/status/{tweet_id}")
                        except Exception as e:
                            print(e)
                            
                    else:
                        print("Mempool insert failure")

                break

        print(f"Run finished, sleeping for {sleep_interval / 60} minutes")
        time.sleep(sleep_interval)
