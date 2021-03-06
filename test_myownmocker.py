#!/usr/bin/env python

import myownmocker
import unittest
import json


class MOMTestCase(unittest.TestCase):

    def setUp(self):
        myownmocker.app.config['TESTING'] = True
        myownmocker.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        self.app = myownmocker.app.test_client()
        self.db = myownmocker.db
        self.db.create_all()

    def tearDown(self):
        self.db.session.remove()
        self.db.drop_all()

    def test_index(self):
        res = self.app.get('/')
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.headers['Location'], 'http://fopina.github.io/myownmocker/')

    def _register(self):
        res = self.app.get('/register/')
        token = None
        if res.status_code == 200:
            j = json.loads(res.data)
            token = j['token']
        return res, token

    def test_register_fail(self):
        try:
            from mock import patch
        except ImportError:
            self.skipTest('requires mock, run: pip install mock')
        with patch('random.SystemRandom.choice', return_value='a'):
            # register once
            res, _ = self._register()
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.headers['Content-Type'], 'application/json')

            # register twice fails
            res, _ = self._register()
            self.assertEqual(res.status_code, 503)
            self.assertEqual(res.headers['Content-Type'], 'application/json')
            j = json.loads(res.data)
            self.assertIn('message', j)
            self.assertEqual(j['message'], 'Unable to generate a token, please try again')

    def test_register(self):
        import string
        from datetime import datetime
        res, token = self._register()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers['Content-Type'], 'application/json')
        self.assertEqual(len(token), 16)
        self.assertEqual(token.strip(string.letters + string.digits), '')
        token_obj = self.db.session.query(myownmocker.MockToken).filter_by(token=token).first()
        self.assertIsNotNone(token_obj)
        self.assertEqual(token_obj.token, token)
        self.assertEqual(token_obj.created_on.date(), datetime.now().date())
        j = json.loads(res.data)
        self.assertIn('setup_url', j)
        self.assertIn('mock_base_url', j)
        self.assertEqual(j['setup_url'], 'http://localhost/setup/%s/' % token)
        self.assertEqual(j['mock_base_url'], 'http://localhost/mock/%s/' % token)
        self.assertEqual(j['setup_secure_url'], 'https://localhost/setup/%s/' % token)
        self.assertEqual(j['mock_base_secure_url'], 'https://localhost/mock/%s/' % token)

    def test_setup_fail_invalid_token(self):
        res = self.app.post('/setup/invalidToken/', data='{"a":"1"}', content_type='application/json')
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.headers['Content-Type'], 'application/json')
        j = json.loads(res.data)
        self.assertIn('message', j)
        self.assertEqual(j['message'], 'Invalid token')

    def test_setup_invalid_json(self):
        _, token = self._register()
        res = self.app.post('/setup/%s/' % token, data='asd', content_type='application/json')
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.headers['Content-Type'], 'application/json')

    def test_setup_missing_field(self):
        _, token = self._register()
        res = self.app.post(
            '/setup/%s/' % token,
            content_type='application/json',
            data=json.dumps({'field': 'value'}),
        )
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.headers['Content-Type'], 'application/json')
        j = json.loads(res.data)
        self.assertEqual(j['message'], 'Missing required field: path')

        res = self.app.post(
            '/setup/%s/' % token,
            content_type='application/json',
            data=json.dumps({'path': 'value'}),
        )
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.headers['Content-Type'], 'application/json')
        j = json.loads(res.data)
        self.assertEqual(j['message'], 'Missing required field: status_code')

    def _setup(self, token, path, status_code, content_type, **kwargs):
        res = self.app.post(
            '/setup/%s/' % token,
            content_type='application/json',
            data=json.dumps({
                'path': path,
                'status_code': status_code,
                'content_type': content_type,
                'custom_headers': kwargs.get('custom_headers', {}),
                'body': kwargs.get('body')
            }),
        )
        return res

    def test_setup(self):
        _, token = self._register()
        res = self._setup(
            token,
            'value',
            200,
            'application/json',
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers['Content-Type'], 'application/json')
        j = json.loads(res.data)
        self.assertEqual(j['message'], 'ok')
        self.assertEqual(j['path_url'], 'http://localhost/mock/%s/value' % token)
        self.assertEqual(j['path_secure_url'], 'https://localhost/mock/%s/value' % token)

    def test_setup_with_slash(self):
        _, token = self._register()
        res = self._setup(
            token,
            '/value',
            200,
            'application/json',
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers['Content-Type'], 'application/json')
        j = json.loads(res.data)
        self.assertEqual(j['message'], 'ok')
        self.assertEqual(j['path_url'], 'http://localhost/mock/%s/value' % token)
        self.assertEqual(j['path_secure_url'], 'https://localhost/mock/%s/value' % token)

    def test_path_invalid(self):
        _, token = self._register()

        res = self.app.get('/mock/%s/my/path/' % token)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.headers['Content-Type'], 'application/json')
        j = json.loads(res.data)
        self.assertEqual(j['message'], 'Method not found')

    def test_path(self):
        _, token = self._register()

        res = self._setup(
            token,
            'value',
            202,
            'application/json',
            body='test',
            custom_headers={
                'X-My-Header': 123,
                'X-My-Header2': 123,
            }
        )
        self.assertEqual(res.status_code, 200)

        res = self.app.get('/mock/%s/value' % token)
        self.assertEqual(res.status_code, 202)
        self.assertEqual(res.headers['Content-Type'], 'application/json')
        self.assertIn('X-My-Header', res.headers)
        self.assertIn('X-My-Header2', res.headers)
        self.assertEqual(res.headers['X-My-Header'], '123')
        self.assertEqual(res.headers['X-My-Header2'], '123')
        self.assertEqual(res.data, 'test')
        return token

    def test_path_resetup(self):
        token = self.test_path()

        # re-setup existing path
        res = self._setup(
            token,
            'value',
            200,
            'text/html',
            body='test2',
            custom_headers={
                'X-My-Header2': 124,
                'X-My-Header3': 124,
            }
        )
        self.assertEqual(res.status_code, 200)

        res = self.app.get('/mock/%s/value' % token)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers['Content-Type'], 'text/html')
        self.assertNotIn('X-My-Header', res.headers)
        self.assertIn('X-My-Header2', res.headers)
        self.assertIn('X-My-Header3', res.headers)
        self.assertEqual(res.headers['X-My-Header2'], '124')
        self.assertEqual(res.headers['X-My-Header3'], '124')
        self.assertEqual(res.data, 'test2')
        return token

    def test_error_500(self):  # for coverage...
        # disable TESTING so the test app processes all exceptions as normal
        myownmocker.app.config['TESTING'] = False
        try:
            from mock import patch
        except ImportError:
            self.skipTest('requires mock, run: pip install mock')
        # screw something up to force error 500
        with patch('random.SystemRandom', return_value=None):
            res, _ = self._register()
            self.assertEqual(res.status_code, 500)
            self.assertEqual(res.headers['Content-Type'], 'application/json')
            j = json.loads(res.data)
            self.assertEqual(j['message'], u"'NoneType' object has no attribute 'choice'")

    def test_purge(self):
        import datetime

        _, token1 = self._register()
        _, token2 = self._register()
        self.assertEqual(self.db.session.query(myownmocker.MockToken).count(), 2)
        self.assertEqual(myownmocker.purge_tokens(), 0)

        t = self.db.session.query(myownmocker.MockToken).filter(myownmocker.MockToken.token == token1).first()
        t.created_on -= datetime.timedelta(days=2)
        self.assertEqual(myownmocker.purge_tokens(), 1)
        self.assertEqual(self.db.session.query(myownmocker.MockToken).count(), 1)


if __name__ == '__main__':
    unittest.main()
