import tornado.ioloop
import tornado.web
import webbrowser
import glob
import json
import os
from tokens_shielded import move_token, generate_token, load_address, tokens_update, load_tokens, load_token_dict, test_db

def get_accounts():
    accounts = []
    paths = glob.glob("shielded_accounts/*")

    for path in paths:
        with open(path) as infile:
            account = json.loads(infile.read())
            accounts.append(account)
    return accounts

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("welcome.html")

class operationsHandler(tornado.web.RequestHandler):
    def get(self):
        accounts = get_accounts()
        self.render("operations.html", accounts=accounts)

class sendHandler(tornado.web.RequestHandler):
    def get(self, data):

        token_name = sendHandler.get_argument(self, "token")
        recipient = sendHandler.get_argument(self, "recipient")
        amount = sendHandler.get_argument(self, "amount")

        #print(token_name, recipient, amount)
        try:
            txdata = move_token(token_name, recipient, amount)

            if amount.isdigit() and token_name.isalnum() and recipient.isalnum():
                self.render("bisurl_send.html", txdata=txdata)
            else:
                self.render("error.html")
        except:
            self.render("error.html")

class generateHandler(tornado.web.RequestHandler):
    def get(self, data):
        token_name = generateHandler.get_argument(self, "token")
        amount = generateHandler.get_argument(self, "amount")
        #recipient = load_address()
        recipient = generateHandler.get_argument(self, "sender")

        #print(token_name, amount)
        txdata = generate_token(token_name=token_name, recipient=recipient, amount=amount)

        if amount.isdigit() and token_name.isalnum():
            self.render("bisurl_generate.html", txdata=txdata)
        else:
            self.render("error.html")


class overviewHandler(tornado.web.RequestHandler):
    def get(self):
        loaded_tokens = load_tokens()

        for token in loaded_tokens:
            token_key_dict = load_token_dict(token=token)
            tokens_update(token_key_dict)

        accounts = get_accounts()
        self.render("overview.html", accounts=accounts)

def make_app():
    return tornado.web.Application([
        (r"/send(.*)", sendHandler),
        (r"/generate(.*)", generateHandler),
        (r"/operations", operationsHandler),
        (r"/overview", overviewHandler),
        (r"/", MainHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(4646)
    test_db()
    webbrowser.open_new_tab("http://127.0.0.1:4646")
    tornado.ioloop.IOLoop.current().start()
