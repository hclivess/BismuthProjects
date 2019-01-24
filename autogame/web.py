import classes
import tornado.ioloop
import tornado.web
import json

dummy = "Waiting for games..."

class GetEnemyHandler(tornado.web.RequestHandler):
    def get(self):

        enemy_objects = []
        enemy_objects_ragnarok = []

        for enemy in classes.Game().enemies:
            enemy_objects.append(enemy())

        for enemy in classes.Game().enemies_ragnarok:
            enemy_objects_ragnarok.append(enemy())

        self.render("enemies.html", title="Enemies", enemies=enemy_objects, enemies_ragnarok = enemy_objects_ragnarok)

class GetWeaponHandler(tornado.web.RequestHandler):
    def get(self):

        weapon_objects = []

        for weapon in classes.Game().weapons:
            weapon_objects.append(weapon())

        self.render("weapons.html", title="Weapons", weapons=weapon_objects)

class GetApiDbHandler(tornado.web.RequestHandler):
    def get(self, hash):
        self.db = classes.ScoreDb()
        self.db.c.execute("SELECT * FROM scores WHERE hash = ?", (hash,))

        self.db_hashes = self.db.c.fetchall()[0]
        print(self.db_hashes)

        api_dict = {}

        api_dict["block_start"] = self.db_hashes[0]
        api_dict["hash"] = self.db_hashes[1]
        api_dict["seed"] = self.db_hashes[2]
        api_dict["experience"] = self.db_hashes[3]
        try:  # Not sure the try is needed, to be checked.
            # decode inventory, stored as a single json-encoded in the db
            api_dict["inventory"] = json.loads(self.db_hashes[4])
        except:
            pass
        api_dict["league"] = self.db_hashes[5]
        api_dict["bet"] = self.db_hashes[6]
        try:  # Not sure the try is needed, to be checked.
            api_dict["damage"] = json.loads(self.db_hashes[7])
        except:
            pass
        try:  # Not sure the try is needed, to be checked.
            api_dict["defense"] = json.loads(self.db_hashes[8])
        except:
            pass
        api_dict["block_end"] = self.db_hashes[9]
        api_dict["finished"] = self.db_hashes[10]

        print(api_dict)
        self.write(json.dumps(api_dict))
        self.set_header('Content-Type', 'application/json')  # send the matching header for paranoid clients
        self.finish()

class GetApiReplayHandler(tornado.web.RequestHandler):
    def get(self, hash):
        with open(f"static/replays/{hash}.json") as file:
            api_dict = json.loads(file.read())
        self.write(json.dumps(list(api_dict.values())))
        self.set_header('Content-Type', 'application/json')  # send the matching header for paranoid clients
        self.finish()

class GetApiSeedHandler(tornado.web.RequestHandler):
    def get(self, seed):
        self.db = classes.ScoreDb()
        self.db.c.execute("SELECT hash FROM scores WHERE seed = ?", (seed,))


        self.db_seed_matches = [h[0] for h in self.db.c.fetchall()]

        self.write(json.dumps(self.db_seed_matches))
        self.set_header('Content-Type', 'application/json')  # send the matching header for paranoid clients
        self.finish()        


class GetTournamentHandler(tornado.web.RequestHandler):
    def get(self, league):
        self.db = classes.ScoreDb()

        #collect pot
        self.db.c.execute("SELECT SUM(bet) FROM scores WHERE league = ? AND finished = ?", (league,1,))
        self.pot_finished = self.db.c.fetchone()[0]
        self.pot_finished = 0 if self.pot_finished is None else self.pot_finished

        self.db.c.execute("SELECT SUM(bet) FROM scores WHERE league = ? AND finished = ?", (league,0,))
        self.pot_unfinished = self.db.c.fetchone()[0]
        self.pot_unfinished = 0 if self.pot_unfinished is None else self.pot_unfinished

        self.pot = self.pot_unfinished + self.pot_finished
        # collect pot

        self.db.c.execute("SELECT * FROM scores WHERE league = ? AND saved = ? ORDER BY experience DESC LIMIT 1", (league,1))
        self.top = self.db.c.fetchone()
        if not self.top:
            self.top = [dummy,"","","","",""]

        self.db.c.execute("SELECT * FROM scores WHERE league = ? AND finished = ? AND saved = ? ORDER BY block_start DESC", (league,1,1,))
        self.all_finished = self.db.c.fetchall()
        if not self.all_finished:
            self.all_finished = [[dummy,"","","","",""]]

        self.db.c.execute("SELECT * FROM scores WHERE league = ? AND finished = ? and saved = ? ORDER BY block_start DESC", (league,0,1,))
        self.all_unfinished = self.db.c.fetchall()
        if not self.all_unfinished:
            self.all_unfinished = [[dummy,"","","","",""]]

        self.render("tournament.html", title=f"{league}", top = self.top, all_finished=self.all_finished, all_unfinished=self.all_unfinished, pot=self.pot)

class GetGameByIdHandler(tornado.web.RequestHandler):

    def get(self, hash):
        with open(f"static/replays/{hash}.json") as file:
            text = json.loads(file.read())
        self.render("replay.html", title="Replay", text=text)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.db = classes.ScoreDb()

        self.db.c.execute("SELECT * FROM scores WHERE saved = ? ORDER BY experience DESC LIMIT 1",(1,))
        self.top = self.db.c.fetchone()
        if not self.top:
            self.top = [dummy,"","","","",""]


        self.db.c.execute("SELECT * FROM scores WHERE finished = ? AND saved = ? ORDER BY block_start DESC",(1,1,))
        self.all_finished = self.db.c.fetchall()
        if not self.all_finished:
            self.all_finished = [[dummy,"","","","",""]]

        self.db.c.execute("SELECT * FROM scores WHERE finished = ? AND saved = ? ORDER BY block_start DESC",(0,1,))
        self.all_unfinished = self.db.c.fetchall()
        if not self.all_unfinished:
            self.all_unfinished = [[dummy,"","","","",""]]

        self.render("main.html", title="Autogame", top = self.top, all_finished=self.all_finished, all_unfinished=self.all_unfinished)


def make_app():

    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "static"}),
        (r"/replay/(.*)", GetGameByIdHandler),
        (r"/enemies", GetEnemyHandler),
        (r"/weapons", GetWeaponHandler),
        (r"/league/(.*)", GetTournamentHandler),

        (r"/api/db/(.*)", GetApiDbHandler),
        (r"/api/replay/(.*)", GetApiReplayHandler),
        (r"/api/seed/(.*)", GetApiSeedHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(6060)
    tornado.ioloop.IOLoop.current().start()
