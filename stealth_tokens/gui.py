import tornado.ioloop
import tornado.web
import webbrowser
import glob
import json
import os
from tokens_stealth import move_token, generate_token, load_address

def get_accounts():
    accounts = []
    paths = glob.glob("stealth_accounts/*")

    for path in paths:
        with open(path) as infile:
            account = json.loads(infile.read())
            accounts.append(account)
    return accounts

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        accounts = get_accounts()
        self.render("operations.html", accounts=accounts)

class sendHandler(tornado.web.RequestHandler):
    def get(self, data):

        token_name = sendHandler.get_argument(self, "token")
        recipient = sendHandler.get_argument(self, "recipient")
        amount = sendHandler.get_argument(self, "amount")

        #print(token_name, recipient, amount)
        txdata = move_token(token_name, recipient, amount)
        self.render("bisurl.html", txdata=txdata)

class generateHandler(tornado.web.RequestHandler):
    def get(self, data):
        token_name = generateHandler.get_argument(self, "token")
        amount = generateHandler.get_argument(self, "amount")
        recipient = load_address()

        #print(token_name, amount)
        txdata = generate_token(token_name=token_name, recipient=recipient, amount=amount)
        self.render("bisurl_generate.html", txdata=txdata)

class overviewHandler(tornado.web.RequestHandler):
    def get(self):
        accounts = get_accounts()
        self.render("overview.html", accounts=accounts)

def make_app():
    return tornado.web.Application([
        (r"/send(.*)", sendHandler),
        (r"/generate(.*)", generateHandler),
        (r"/overview", overviewHandler),
        (r"/", MainHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(4646)
    webbrowser.open_new_tab("http://127.0.0.1:4646")
    tornado.ioloop.IOLoop.current().start()
