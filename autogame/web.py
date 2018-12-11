import classes
import tornado.ioloop
import tornado.web
import json

dummy = "Waiting for games..."

class GetBeastHandler(tornado.web.RequestHandler):
    def get(self):

        enemy_objects = []
        for enemy in classes.Game().enemies:
            enemy_objects.append(enemy())

        self.render("enemies.html", title="Beasts", enemies=enemy_objects)

class GetTournamentHandler(tornado.web.RequestHandler):
    def get(self, league):
        self.db = classes.ScoreDb()

        self.db.c.execute("SELECT SUM(bet) FROM scores WHERE league = ?", (league,))
        self.pot_finished = self.db.c.fetchone()[0]
        self.pot_finished = 0 if self.pot_finished is None else self.pot_finished

        self.db.c.execute("SELECT SUM(bet) FROM unfinished WHERE league = ?", (league,))
        self.pot_unfinished = self.db.c.fetchone()[0]
        self.pot_unfinished = 0 if self.pot_unfinished is None else self.pot_unfinished


        self.pot = self.pot_unfinished + self.pot_finished

        self.db.c.execute("SELECT * FROM scores WHERE league = ? ORDER BY experience DESC LIMIT 1", (league,))
        self.top = self.db.c.fetchone()
        if not self.top:
            self.top = [dummy,"","","","",""]

        self.db.c.execute("SELECT * FROM scores WHERE league = ? ORDER BY block_start DESC", (league,))
        self.all_finished = self.db.c.fetchall()
        if not self.all_finished:
            self.all_finished = [[dummy,"","","","",""]]

        self.db.c.execute("SELECT * FROM unfinished WHERE league = ? ORDER BY block_start DESC", (league,))
        self.all_unfinished = self.db.c.fetchall()
        if not self.all_unfinished:
            self.all_unfinished = [[dummy,"","","","",""]]

        self.render("tournament.html", title=f"{league}", top = self.top, all_finished=self.all_finished, all_unfinished=self.all_unfinished, pot=self.pot)

class GetGameByIdHandler(tornado.web.RequestHandler):

    def get(self, hash):
        with open(f"static/replays/{hash}.json") as file:
            text = json.loads(file.read())
        self.render("replay.html", title="Replay", text=text)

class GetUnfinishedByIdHandler(tornado.web.RequestHandler):

    def get(self, hash):
        with open(f"static/replays/unfinished/{hash}.json") as file:
            text = json.loads(file.read())
        self.render("unfinished.html", title="Replay", text=text)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.db = classes.ScoreDb()

        self.db.c.execute("SELECT * FROM scores ORDER BY experience DESC LIMIT 1")
        self.top = self.db.c.fetchone()
        if not self.top:
            self.top = [dummy,"","","","",""]


        self.db.c.execute("SELECT * FROM scores ORDER BY block_start DESC")
        self.all_finished = self.db.c.fetchall()
        if not self.all_finished:
            self.all_finished = [[dummy,"","","","",""]]

        self.db.c.execute("SELECT * FROM unfinished ORDER BY block_start DESC")
        self.all_unfinished = self.db.c.fetchall()
        if not self.all_unfinished:
            self.all_unfinished = [[dummy,"","","","",""]]

        self.render("main.html", title="Autogame", top = self.top, all_finished=self.all_finished, all_unfinished=self.all_unfinished)


def make_app():

    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "static"}),
        (r"/replay/(.*)", GetGameByIdHandler),
        (r"/unfinished/(.*)", GetUnfinishedByIdHandler),
        (r"/enemies", GetBeastHandler),
        (r"/league/(.*)", GetTournamentHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(6060)
    tornado.ioloop.IOLoop.current().start()