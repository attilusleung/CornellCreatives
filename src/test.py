import unittest
import json
import requests

LOCAL = 'http://localhost:5000'

class TestRoutes(unittest.TestCase):
    def test_root(self):
        pass
        #assert requests.get(LOCAL + '/') == 'Hello World!'

    def reset(self):
        assert requests.post(LOCAL + '/reset/') == 'True'

    def test_register_no_avatar(self):
        r = requests.post(LOCAL + '/register/', data = json.dumps({
            'netid': 'yl787',
            'password': 'pass'
        }))
        r = r.json()['data']
        assert r.get('success')
        assert r.get('netid') == 'yl787'
        assert r.get('avatar') == 0
        assert r.get('services') == []
        #assert r.get('tracking') == []
        assert 'session' in r
        assert 'expiration' in r
        assert 'renew' in r

    def test_register_with_avatar(self):
        r = json.loads(requests.post(LOCAL + '/register/', data = json.dumps({
            'netid': 'gj75',
            'password': 'pass',
            'avatar': 1
        })))
        assert r.get('success')
        assert r.get('netid') == 'gj75'
        assert r.get('avatar') == 1
        assert r.get('services') == []
        assert r.get('tracking') == []
        assert 'session' in r
        assert 'expiration' in r
        assert 'renew' in r

    def reset_again(self):
        assert requests.post(LOCAL + '/reset/') == 'True'

    def test_login(self):
        p = json.loads(LOCAL + '/register/', data = requests.post(json.dumps({
            'netid': 'yl787',
            'password': 'pass'
        })))
        r = requests.post(LOCAL + '/login/', data = requests.post(json.dumps({
            'netid': 'yl787',
            'password': 'pass'
        })))
        assert r.get('success')
        assert 'session' in r
        assert 'expiration' in r
        assert 'renew' in r

if __name__ == '__main__':
    unittest.main()
