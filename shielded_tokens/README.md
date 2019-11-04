# Bismuth shielded token interface

This interface runs on Tornado. It is designed to be portable. It newly uses json instead of a database for data storage.

## Configuration
You need to adjust path to your Bismuth ledger in config.txt

## How to run

Run `gui.py` for the interface. It will open automatically at [http://localhost:4646](http://localhost:4646). From there, you
will be able to access the menus for token generation and transfers. 

Upon token generation, a specific `json` file will be generated in the `shielded_keys` menu. You need to copy this file on 
any node that you want to decrypt the token.

## Dev integration
See `tokens_shielded.py`, the basic sequence is in `__main__`