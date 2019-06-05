import json
import tornado.ioloop
import tornado.web
import dator
import threading
import time

class MainHandler(tornado.web.RequestHandler):
    def initialize(self, updater):
        self.updater = updater
        #self.updater.update()

    def get(self):
        #call fetcher
        self.updater.update()

        #render
        self.render("chart.html",
                    stata = self.updater.history.stata,
                    )

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler, {'updater': updater}),
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "static"}),
    ])

class ThreadedClient(threading.Thread):
    def __init__(self, updater):
        threading.Thread.__init__(self)

    def run(self):
       while True:
           updater.update()
           time.sleep(10)



if __name__ == "__main__":
    updater = dator.Updater()

    background = ThreadedClient(updater)
    background.start()


    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()


