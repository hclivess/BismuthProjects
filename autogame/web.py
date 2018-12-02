import classes
import tornado.ioloop
import tornado.web


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.db = classes.ScoreDb()

        self.db.c.execute("SELECT * FROM scores ORDER BY experience LIMIT 1")
        self.top = self.db.c.fetchone()
        block_start = self.top[0]
        hash = self.top[1]
        seed = self.top[2]
        experience = self.top[3]
        inventory = self.top[4]

        self.write("<h1>Top Player:</h1>")

        self.write(f"Game start:{block_start}<br>")
        self.write(f"Game hash:{hash}<br>")
        self.write(f"Game seed:{seed}<br>")
        self.write(f"Hero experience:{experience}<br>")
        self.write(f"Hero inventory:{inventory}<br>")

        self.db.c.execute("SELECT * FROM scores")
        self.all = self.db.c.fetchall()
        self.write("<h1>Finished Games:</h1>")
        for line in self.all:
            self.write(str(line))
            self.write("<br>")

def make_app():

    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "static"}),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(80)
    tornado.ioloop.IOLoop.current().start()