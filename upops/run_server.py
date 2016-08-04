import os
import django.core.handlers.wsgi
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import tornado.httpserver
from tornado.websocket import WebSocketClosedError
from tornado.options import define, options, parse_command_line
from django.core.wsgi import get_wsgi_application
import tornado.wsgi
import tornado.httpclient
import time

os.environ['DJANGO_SETTINGS_MODULE'] = 'upops.settings'

define("port", default=8000, help="run on the given port", type=int)
define("host", default="10.200.0.181", help="run port on given host", type=str)


class DbImportTest(tornado.web.RequestHandler):
    def get(self):
        for result in range(100):
            time.sleep(2)
        self.render("updbm/importdb.html", result=result)


def main():
    parse_command_line()
    wsgi_app = tornado.wsgi.WSGIContainer(django.core.handlers.wsgi.WSGIHandler())
    setting = {
        'template_path': os.path.join(os.path.dirname(__file__), 'templates'),
        'static_path': os.path.join(os.path.dirname(__file__), 'static'),
        'debug': True,
    }

    tornado_app = tornado.web.Application(
        [   (r'/wc/dbtest/', DbImportTest),
            (r"/static/(.*)", tornado.web.StaticFileHandler,
             dict(path=os.path.join(os.path.dirname(__file__), "static"))),
            ('.*', tornado.web.FallbackHandler, dict(fallback=wsgi_app)),
        ], **setting)

    server = tornado.httpserver.HTTPServer(tornado_app)
    server.listen(options.port)

    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()

