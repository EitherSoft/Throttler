import tornadoredis
from tornado.web import Application
from tornado.ioloop import IOLoop
from tornado.options import options
from handler import DelayHandler
from settings import settings, REDIS


class ThrottleApp(Application):
    redis = None

    def __init__(self, *args, **kwargs):
        db = tornadoredis.Client(**REDIS)
        db.connect()

        urls = (
            (r"/delay", DelayHandler),
        )

        super(ThrottleApp, self).__init__(urls, db=db, *args, **dict(settings, **kwargs))


def main():
    app = ThrottleApp()
    app.listen(options.port)
    IOLoop.instance().start()


if __name__ == '__main__':
    main()
