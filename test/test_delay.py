import json
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
    def test_domain_delay(self):
        client = AsyncHTTPClient(self.io_loop)
        response = yield client.fetch('http://127.0.0.1:5000/delay?domain=google.com', method='DELETE')
        self.assertIn('"success": true', response.body)

        response = yield client.fetch(
            'http://127.0.0.1:5000/delay', method='POST', body='{"domain": "google.com", "duration": 300, "limit": 10}'
        )
        self.assertIn('"success": true', response.body)

        response = yield client.fetch('http://127.0.0.1:5000/delay?domain=google.com&request_time=2.5')
        body = json.loads(response.body)
        self.assertTrue('timeout' in body)
        self.assertTrue(float(body['timeout']))
        timeout = float(body['timeout'])
        self.assertEqual(27.5, round(timeout, 1))

        response = yield client.fetch('http://127.0.0.1:5000/delay?domain=google.com&request_time=2')
        body = json.loads(response.body)
        self.assertTrue('timeout' in body)
        self.assertTrue(float(body['timeout']))
        timeout = float(body['timeout'])
        self.assertEqual(55.5, round(timeout, 1))

        response = yield client.fetch('http://127.0.0.1:5000/delay?domain=google.com&request_time=1.5')
        body = json.loads(response.body)
        self.assertTrue('timeout' in body)
        self.assertTrue(float(body['timeout']))
        timeout = float(body['timeout'])
        self.assertEqual(84.0, round(timeout, 1))
