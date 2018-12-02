import classes
import tornado.ioloop
import tornado.web


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.db = classes.ScoreDb()

        self.db.c.execute("SELECT * FROM scores ORDER BY experience LIMIT 1")
        self.top = self.db.c.fetchone()

        self.write('<title>Autogame</title>\n')
        # html.append('<link rel="stylesheet" type="text/css" href="static/style.css">')
        self.write('<link rel = "icon" href = "static/explorer.ico" type = "image/x-icon" / >\n')
        self.write('<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" >')
        self.write('<script src="static/Chart.js"></script>\n')
        self.write('<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>')
        self.write('<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script >')


        self.write("<h1>Top Player:</h1>")
        self.write("<table class='table table-responsive'>")
        self.write("<tr>")
        self.write("<th>Start block</th>")
        self.write("<th>Game hash</th>")
        self.write("<th>Game seed</th>")
        self.write("<th>Hero experience</th>")
        self.write("<th>Corpse inventory</th>")
        self.write("</tr>")

        self.write("<tr>")
        self.write(f"<td>{self.top[0]}")
        self.write(f"<td>{self.top[1]}")
        self.write(f"<td>{self.top[2]}")
        self.write(f"<td>{self.top[3]}")
        self.write(f"<td>{self.top[4]}")
        self.write("</td></tr>")

        self.write("</table>")


        self.db.c.execute("SELECT * FROM scores")
        self.all = self.db.c.fetchall()
        self.write("<h1>Finished Games:</h1>")

        self.write("<table class='table table-responsive'>")
        self.write("<tr>")
        self.write("<th>Start block</th>")
        self.write("<th>Game hash</th>")
        self.write("<th>Game seed</th>")
        self.write("<th>Hero experience</th>")
        self.write("<th>Corpse inventory</th>")
        self.write("</tr>")

        for line in self.all:
            self.write("<tr>")
            self.write(f"<td>{line[0]}")
            self.write(f"<td>{line[1]}")
            self.write(f"<td>{line[2]}")
            self.write(f"<td>{line[3]}")
            self.write(f"<td>{line[4]}")
            self.write("</td></tr>")

        self.write("</table>")


def make_app():

    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "static"}),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(80)
    tornado.ioloop.IOLoop.current().start()