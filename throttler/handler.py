import json
import time
from tornado import web
from tornado import gen


class DelayHandler(web.RequestHandler):
    db = None

    def initialize(self, **kwargs):
        self.db = self.settings['db']

    @web.asynchronous
    @gen.engine
    def get(self, *args, **kwargs):
        domain = self.get_argument('domain')
        request_time = float(self.get_argument('request_time'))

        domain_settings = yield gen.Task(self._prepare_domain_settings, domain)

        key = 'request_time:%s:%i:%i' % (
            domain,
            domain_settings['duration'],
            time.time() // domain_settings['duration']
        )

        count = yield gen.Task(self.db.incr, key)

        yield gen.Task(self.db.expire, key, int(domain_settings['duration']))

        timeout = yield gen.Task(self._get_timeout, count, request_time, **domain_settings)

        self.set_header('Content-Type', 'application/json')
        self.finish(json.dumps({
            'timeout': timeout
        }))

    @web.asynchronous
    @gen.engine
    def post(self, *args, **kwargs):
        data = json.loads(self.request.body)

        domain = data.get('domain', None)
        duration = float(data.get('duration', self.settings['duration']))
        limit = float(data.get('limit', self.settings['limit']))

        request_timeout = round(duration / limit, 3)

        result = yield gen.Task(self.db.hmset, 'limits:%s' % domain, {
            'duration': duration,
            'limit': limit,
            'request_timeout': request_timeout
        })

        self.set_header('Content-Type', 'application/json')
        self.finish(json.dumps({
            'success': True if result else False
        }))

    @gen.engine
    def _prepare_domain_settings(self, domain, callback):
        domain_settings = yield gen.Task(self.db.hmget, 'limits:%s' % domain, ['duration', 'limit', 'request_timeout'])

        if domain_settings['duration'] and domain_settings['limit'] and domain_settings['request_timeout']:
            for k, v in domain_settings.iteritems():
                domain_settings[k] = float(v)
        else:
            domain_settings = {
                'duration': self.settings['duration'],
                'limit': self.settings['limit'],
                'request_timeout': round(float(self.settings['duration']) / self.settings['limit'])
            }

        callback(domain_settings)

    @gen.engine
    def _get_timeout(self, count, request_time, limit, duration, request_timeout, callback):
        if count >= limit:
            timeout = duration
        else:
            timeout = request_timeout - request_time
            if timeout < 0:
                timeout = 0

        callback(timeout)
