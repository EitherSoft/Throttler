import json
import time
from tornado import web
from tornado import gen


class DelayHandler(web.RequestHandler):
    db = None
    calculate_next_request_time = None

    def initialize(self, **kwargs):
        self.db = self.settings['db']
        self.calculate_next_request_time = self.settings['calculate_next_request_time']

    @web.asynchronous
    @gen.engine
    def get(self, *args, **kwargs):
        domain = self.get_argument('domain')
        last_request_time = float(self.get_argument('request_time'))

        domain_settings = yield gen.Task(self._prepare_domain_settings, domain)

        key = 'next_request_time:%s' % domain

        next_request_time = yield gen.Task(
            self.db.eval,
            self.calculate_next_request_time,
            [key],
            [domain_settings['request_timeout'], last_request_time, time.time()]
        )

        timeout = round(float(next_request_time) - time.time(), 3)

        self.set_header('Content-Type', 'application/json')
        self.finish(json.dumps({
            'timeout': timeout if timeout > 0 else 0
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
