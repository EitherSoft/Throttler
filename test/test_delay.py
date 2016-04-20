import tornado
import tornadoredis
from tornado.httpclient import AsyncHTTPClient
from tornado.testing import AsyncTestCase
from throttler.settings import REDIS


class TestDelay(AsyncTestCase):
    def setUp(self):
        db = tornadoredis.Client(**REDIS)
        db.connect()
        db.flushall()

        super(TestDelay, self).setUp()

    @tornado.testing.gen_test
    def test_http_fetch(self):
        client = AsyncHTTPClient(self.io_loop)
        response = yield client.fetch('http://127.0.0.1:5000/delay', method='POST', body='{"domain": "google.com"}')
        # Test contents of response
        self.assertIn('"success": true', response.body)

        for x in xrange(1, 10):
            response = yield client.fetch('http://127.0.0.1:5000/delay?domain=google.com&request_time=2.54')
            # Test contents of response
            self.assertIn('"timeout": 27.46', response.body)

        response = yield client.fetch('http://127.0.0.1:5000/delay?domain=google.com&request_time=2.54')
        # Test contents of response
        self.assertIn('"timeout": 300', response.body)
