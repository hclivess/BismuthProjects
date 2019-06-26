import json
import tornado.ioloop
import tornado.web
import dator
import threading
import time

class difficultyHandler(tornado.web.RequestHandler):
    def initialize(self, updater):
        self.updater = updater
        #self.updater.update()

    def get(self):
        #call fetcher
        #self.updater.update()

        #render

        y_axis = []
        x_axis = []

        for block, data in self.updater.history.blocks.items():
            print(block)
            print(data)

            x_axis.append(int(block))
            y_axis.append(float(data['mining_tx']['difficulty']))

        self.render("chart.html",
                    y_axis = y_axis,
                    x_axis = x_axis,
                    y_label="Difficulty",
                    x_label="Block")


class block_timestampsHandler(tornado.web.RequestHandler):
    def initialize(self, updater):
        self.updater = updater
        #self.updater.update()

    def get(self):
        #call fetcher
        #self.updater.update()

        #render

        y_axis = []
        x_axis = []

        for block, data in self.updater.history.blocks.items():
            x_axis.append(int(block))
            y_axis.append(float(data['mining_tx']['timestamp']))

        self.render("chart.html",
                    y_axis = y_axis,
                    x_axis = x_axis,
                    y_label="Timestamp",
                    x_label="Block")

class tx_timestampsHandler(tornado.web.RequestHandler):
    def initialize(self, updater):
        self.updater = updater
        #self.updater.update()

    def get(self):
        #call fetcher
        #self.updater.update()

        #render

        y_axis = []
        x_axis = []

        for block, data in self.updater.history.blocks.items():
            print(block)
            print(data)

            x_axis.append(int(block))
            for transaction in data['transactions']:
                y_axis.append(float(transaction['timestamp']))

        self.render("chart.html",
                    y_axis = y_axis,
                    x_axis = x_axis,
                    y_label="Timestamp",
                    x_label="Block")

class connectionsHandler(tornado.web.RequestHandler):
    def initialize(self, updater):
        self.updater = updater
        #self.updater.update()

    def get(self):
        #call fetcher
        #self.updater.update()

        #render

        y_axis = []
        x_axis = []

        for x in range(len(self.updater.history.stata)):
            x_axis.append(int(x))

        for items in self.updater.history.stata:
            for subitem in items:
                y_axis.append(subitem['connections'])

        self.render("chart.html",
                    y_axis = y_axis,
                    x_axis = x_axis,
                    y_label="Connections",
                    x_label="Interval")

class consensusHandler(tornado.web.RequestHandler):
    def initialize(self, updater):
        self.updater = updater
        #self.updater.update()

    def get(self):
        #call fetcher
        #self.updater.update()

        #render
        

        y_axis = []
        x_axis = []

        for x in range(len(self.updater.history.stata)):
            x_axis.append(int(x))

        for items in self.updater.history.stata:
            for subitem in items:
                y_axis.append(subitem['consensus'])

        self.render("chart.html",
                    y_axis = y_axis,
                    x_axis = x_axis,
                    y_label="Consensus",
                    x_label="Interval")

class consensus_percentHandler(tornado.web.RequestHandler):
    def initialize(self, updater):
        self.updater = updater
        #self.updater.update()

    def get(self):
        #call fetcher
        #self.updater.update()

        #render
        

        y_axis = []
        x_axis = []

        for x in range(len(self.updater.history.stata)):
            x_axis.append(int(x))

        for items in self.updater.history.stata:
            for subitem in items:
                y_axis.append(subitem['consensus_percent'])

        self.render("chart.html",
                    y_axis = y_axis,
                    x_axis = x_axis,
                    y_label="Consensus Percentage",
                    x_label="Interval")


class threadsHandler(tornado.web.RequestHandler):
    def initialize(self, updater):
        self.updater = updater
        #self.updater.update()

    def get(self):
        #call fetcher
        #self.updater.update()


        #render
        

        y_axis = []
        x_axis = []

        for x in range(len(self.updater.history.stata)):
            x_axis.append(int(x))

        for items in self.updater.history.stata:
            for subitem in items:
                y_axis.append(subitem['threads'])

        self.render("chart.html",
                    y_axis = y_axis,
                    x_axis = x_axis,
                    y_label="Threads",
                    x_label="Interval")

class diff_droppedHandler(tornado.web.RequestHandler):
    def initialize(self, updater):
        self.updater = updater
        #self.updater.update()

    def get(self):
        #call fetcher
        #self.updater.update()

        #render

        y_axis = []
        x_axis = []

        for item in self.updater.history.diffs:
            for block, difficulty in item.items():
                x_axis.append(int(block))

        for item in self.updater.history.diffs:
            for block, difficulty in item.items():
                y_axis.append(difficulty['diff_dropped'])

        self.render("chart.html",
                    y_axis = y_axis,
                    x_axis = x_axis,
                    y_label="Difficulty After Readjustment",
                    x_label="Interval")

class block_timeHandler(tornado.web.RequestHandler):
    def initialize(self, updater):
        self.updater = updater
        #self.updater.update()

    def get(self):
        #call fetcher
        #self.updater.update()

        #render


        y_axis = []
        x_axis = []

        for item in self.updater.history.diffs:
            for block, difficulty in item.items():
                x_axis.append(int(block))

        for item in self.updater.history.diffs:
            for block, difficulty in item.items():
                y_axis.append(difficulty['block_time'])

        self.render("chart.html",
                    y_axis = y_axis,
                    x_axis = x_axis,
                    y_label="Block Time",
                    x_label="Interval")

class time_to_generateHandler(tornado.web.RequestHandler):
    def initialize(self, updater):
        self.updater = updater
        #self.updater.update()

    def get(self):
        #call fetcher
        #self.updater.update()

        #render
        

        y_axis = []
        x_axis = []

        for item in self.updater.history.diffs:
            for block, difficulty in item.items():
                x_axis.append(int(block))

        for item in self.updater.history.diffs:
            for block, difficulty in item.items():
                y_axis.append(difficulty['time_to_generate'])

        self.render("chart.html",
                    y_axis = y_axis,
                    x_axis = x_axis,
                    y_label="Seconds",
                    x_label="Interval")

class diff_adjustmentHandler(tornado.web.RequestHandler):
    def initialize(self, updater):
        self.updater = updater
        #self.updater.update()

    def get(self):
        #call fetcher
        #self.updater.update()

        #render
        

        y_axis = []
        x_axis = []

        for item in self.updater.history.diffs:
            for block, difficulty in item.items():
                x_axis.append(int(block))

        for item in self.updater.history.diffs:
            for block, difficulty in item.items():
                y_axis.append(difficulty['diff_adjustment'])

        self.render("chart.html",
                    y_axis = y_axis,
                    x_axis = x_axis,
                    y_label = "Difficulty Readjustment",
                    x_label = "Interval (min. 1 block)")

class hashrateHandler(tornado.web.RequestHandler):
    def initialize(self, updater):
        self.updater = updater
        #self.updater.update()

    def get(self):
        #call fetcher
        #self.updater.update()

        y_axis = []
        x_axis = []

        for item in self.updater.history.diffs:
            for block, difficulty in item.items():
                x_axis.append(int(block))

        for item in self.updater.history.diffs:
            for block, difficulty in item.items():
                y_axis.append(difficulty['hashrate'])

        self.render("chart.html",
                    y_axis = y_axis,
                    x_axis = x_axis,
                    y_label = "Hashrate",
                    x_label = "Interval (min. 1 block)")

class statsHandler(tornado.web.RequestHandler):
    def initialize(self, updater):
        self.updater = updater
        #self.updater.update()

    def get(self):
        #call fetcher
        #self.updater.update()


        self.render("stats.html",
                    stata = self.updater.history.stata
                    )

def make_app():
    return tornado.web.Application([
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "static"}),
        (r"/difficulty", difficultyHandler, {'updater': updater}),
        (r"/block_timestamps", block_timestampsHandler, {'updater': updater}),
        (r"/tx_timestamps", tx_timestampsHandler, {'updater': updater}),
        (r"/connections", connectionsHandler, {'updater': updater}),
        (r"/consensus", consensusHandler, {'updater': updater}),
        (r"/consensus_percent", consensus_percentHandler, {'updater': updater}),
        (r"/threads", threadsHandler, {'updater': updater}),
        (r"/diff_dropped", diff_droppedHandler, {'updater': updater}),
        (r"/block_time", block_timeHandler, {'updater': updater}),
        (r"/time_to_generate", time_to_generateHandler, {'updater': updater}),
        (r"/diff_adjustment", diff_adjustmentHandler, {'updater': updater}),
        (r"/hashrate", hashrateHandler, {'updater': updater}),
        (r"/", statsHandler, {'updater': updater}),
    ])

class ThreadedClient(threading.Thread):
    def __init__(self, updater):
        threading.Thread.__init__(self)

    def run(self):
       while True:
           updater.update()
           time.sleep(360)



if __name__ == "__main__":
    updater = dator.Updater()

    background = ThreadedClient(updater)
    background.start()


    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()


