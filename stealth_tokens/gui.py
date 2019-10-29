import tornado.ioloop
import tornado.web
import webbrowser
import glob
import json
import os

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
        self.render("gui.html", accounts=accounts)

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])



if __name__ == "__main__":
    app = make_app()
    app.listen(4646)
    webbrowser.open_new_tab("http://127.0.0.1:4646")
    tornado.ioloop.IOLoop.current().start()
