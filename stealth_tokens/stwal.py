import tornado.ioloop
import tornado.web
import json
from bismuthclient import bismuthmultiwallet
from tokens_stealth import *

class Persistent():
    def __init__(self):
        self.wallet = None


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

class KeysHandler(tornado.web.RequestHandler):
    def get(self):
        with open("token_keys.json") as file:
            token_keys = json.loads(file.read())
        self.write(token_keys)

class LoadWallet(tornado.web.RequestHandler):
    def get(self):
        persistent.wallet = bismuthmultiwallet.BismuthMultiWallet()
        try:
            persistent.wallet.import_der("wallet.der")
        except:
            pass

        persistent.wallet.load()

        self.write(persistent.wallet._data)

def make_app():
    return tornado.web.Application([
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "static"}),
        (r"/", MainHandler, {'persistent': persistent}),
        (r"/keys", KeysHandler, {'persistent': persistent}),
        (r"/load_wallet", LoadWallet, {'persistent': persistent}),
    ])

if __name__ == "__main__":
    persistent = Persistent()
    app = make_app()
    app.listen(6768)
    tornado.ioloop.IOLoop.current().start()