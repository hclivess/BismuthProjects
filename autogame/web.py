import classes
import tornado.ioloop
import tornado.web
import json

class GetGameByIdHandler(tornado.web.RequestHandler):

    def get(self, hash):
        #url args
        finished_arg = self.get_arguments("finished")
        print (finished_arg)
        if finished_arg[0] == "1":
            finished = True
        else:
            finished = False
        # url args

        if finished:
            filename = (f"static/replays/{hash}.json")
        else:
            filename = (f"static/replays/{hash}_.json")

        with open (filename) as file:
            text = json.loads(file.read())

            display = ""
            for key, value in text.items():
                display += "<p>"
                display += value
                display += "</p>"

        with open("static/html1") as file:
            self.write(file.read())

        self.write(display)

        #style
        self.write("<style>")
        with open("static/style.css") as file:
            self.write(file.read())

        if finished:
            for key, value in text.items():
                self.write("\n")
                self.write("p:nth-child("+str(key)+"){white-space:nowrap;overflow:hidden;opacity:0;animation: type 1s steps(40, end);animation: type2 1s steps(40, end);animation-fill-mode: forwards;animation-delay: "+str(int(key)*2)+"s;}")
                self.write("\n")
        self.write("</style>")
        # style

        with open("static/html2") as file:
            self.write(file.read())



class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.db = classes.ScoreDb()

        self.db.c.execute("SELECT * FROM scores ORDER BY experience DESC LIMIT 1")
        self.top = self.db.c.fetchone()

        self.write('<title>Autogame</title>\n')

        # html.append('<link rel="stylesheet" type="text/css" href="static/style.css">')
        self.write('<link rel = "icon" href = "static/explorer.ico" type = "image/x-icon" / >\n')
        self.write('<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" >')

        self.write('<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>')
        self.write('<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script >')



        self.write("<h1>Top Player:</h1>")
        self.write("<table class='table table-responsive'>")
        self.write("<tr>")
        self.write("<th>Start block</th>")
        self.write("<th>Game replay</th>")
        self.write("<th>Game seed</th>")
        self.write("<th>Hero experience</th>")
        self.write("<th>Corpse inventory</th>")
        self.write("</tr>")

        self.write("<tr>")
        self.write(f"<td>{self.top[0]}")
        self.write(f"<td><a href='/replay/{self.top[1]}?finished=1'>{self.top[1]}</a>")
        self.write(f"<td>{self.top[2]}")
        self.write(f"<td>{self.top[3]}")
        self.write(f"<td>{self.top[4]}")
        self.write("</td></tr>")

        self.write("</table>")


        self.db.c.execute("SELECT * FROM scores")
        self.all_finished = self.db.c.fetchall()
        self.write("<h1>Finished Games:</h1>")

        #table
        self.write("<table class='table table-responsive'>")
        self.write("<tr>")
        self.write("<th>Start block</th>")
        self.write("<th>Game replay</th>")
        self.write("<th>Game seed</th>")
        self.write("<th>Hero experience</th>")
        self.write("<th>Corpse inventory</th>")
        self.write("</tr>")

        for line in self.all_finished:
            self.write("<tr>")
            self.write(f"<td>{line[0]}")
            self.write(f"<td><a href='/replay/{line[1]}?finished=1'>{line[1]}</a>")
            self.write(f"<td>{line[2]}")
            self.write(f"<td>{line[3]}")
            self.write(f"<td>{line[4]}")
            self.write("</td></tr>")

        self.write("</table>")
        # table


        self.db.c.execute("SELECT * FROM unfinished")
        self.all_unfinished = self.db.c.fetchall()

        self.write("<h1>Games in progress:</h1>")
        #table
        self.write("<table class='table table-responsive'>")
        self.write("<tr>")
        self.write("<th>Start block</th>")
        self.write("<th>Game replay</th>")
        self.write("<th>Game seed</th>")
        self.write("<th>Hero experience</th>")
        self.write("<th>Hero inventory</th>")
        self.write("</tr>")

        for line in self.all_unfinished:
            self.write("<tr>")
            self.write(f"<td>{line[0]}")
            self.write(f"<td><a href='/replay/{line[1]}?finished=0'>{line[1]}</a>")
            self.write(f"<td>{line[2]}")
            self.write(f"<td>{line[3]}")
            self.write(f"<td>{line[4]}")
            self.write("</td></tr>")

        self.write("</table>")
        # table


def make_app():

    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "static"}),
        (r"/replay/(.*)", GetGameByIdHandler),
        (r"/unfinished/(.*)", GetGameByIdHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(6060)
    tornado.ioloop.IOLoop.current().start()