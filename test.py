import jwt
import datetime
import requests
from pprint import pprint

import db
import conf


origin = 'http://localhost:{}'.format(conf.port)


def describe(message):
    print '-' * 20, message


def get(path, cookies={}):
    return requests.get(origin + path, cookies=cookies)


def post(path, data, cookies={}):
    return requests.post(origin + path, json=data, cookies=cookies)


def put(path, data, cookies={}):
    return requests.put(origin + path, json=data, cookies=cookies)


def delete(path, cookies={}):
    return requests.delete(origin + path, cookies=cookies)


with open('/home/fans656/token') as f:
    token = f.read().strip()
cookies = {'token': token}


def test_basic():
    db.getdb().note.remove({})

    describe('guest post note')
    assert post('/note', {'foo': 'bar'}).status_code == 401

    describe('post note')
    r = post('/note', {'foo': 'bar'}, cookies=cookies)
    assert r.status_code == 200

    describe('verify note posted')
    r = get('/note/1')
    assert r.status_code == 200
    note = r.json()
    assert 'ctime' in note
    assert 'mtime' in note
    assert note['id'] == 1
    assert note['foo'] == 'bar'

    describe('guest put note')
    r = put('/note/1', {'foo': '!!!'})
    assert r.status_code == 401

    describe('put note')
    r = put('/note/1', {'foo': '!!!'}, cookies=cookies)
    assert r.status_code == 200

    describe('verify note changed')
    r = get('/note/1')
    assert r.json()['foo'] == '!!!'

    describe('guest delete')
    assert delete('/note/1').status_code == 401

    describe('delete')
    assert delete('/note/1', cookies=cookies).status_code == 200

    describe('verify deleted')
    assert get('/note/1').status_code == 404


def test_hidden():
    db.getdb().note.remove({})

    describe('post a hidden note')
    r = post('/note', {'foo': 'bar', 'tags': ['.', 't']}, cookies=cookies)
    assert r.status_code == 200

    describe('guest should got 404')
    r = get('/note/1')
    assert r.status_code == 404

    describe('me should got fine')
    r = get('/note/1', cookies=cookies)
    assert r.status_code == 200

    describe('guest query should not include hidden')
    r = post('/query', {})
    assert r.json()['notes'] == []

    describe('me query should include hidden')
    r = post('/query', {}, cookies=cookies)
    assert len(r.json()['notes']) == 1


def test_pagination():
    db.getdb().note.remove({})

    now = datetime.datetime.now() - datetime.timedelta(days=365)
    for i in xrange(11):
        note = {
            'count': i + 1,
            'ctime': datetime.datetime.strftime(now, '%Y-%m-%d %H:%M:%S UTC'),
        }
        post('/note', note, cookies=cookies)
        now += datetime.timedelta(days=1)

    describe('default query')
    res = post('/query', {}).json()
    assert res['total'] == 11
    assert res['page'] == 1
    assert res['size'] == 20

    describe('query page 1')
    res = post('/query?page=1&size=5', {}).json()
    assert res['total'] == 11
    assert res['page'] == 1
    assert res['size'] == 5
    notes = res['notes']
    assert notes[0]['id'] == 11 and notes[-1]['id'] == 7

    describe('query page 2')
    res = post('/query?page=2&size=5', {}).json()
    assert res['total'] == 11
    assert res['page'] == 2
    assert res['size'] == 5
    notes = res['notes']
    assert notes[0]['id'] == 6 and notes[-1]['id'] == 2

    describe('query page 3')
    res = post('/query?page=3&size=5', {}).json()
    assert res['total'] == 11
    assert res['page'] == 3
    assert res['size'] == 5
    notes = res['notes']
    assert notes[0]['id'] == notes[-1]['id'] == 1

    describe('query page 4')
    res = post('/query?page=4&size=5', {}).json()
    assert res['total'] == 11
    assert res['page'] == 4
    assert res['size'] == 5
    assert not res['notes']

    describe('make some note hidden')
    note = get('/note/2').json()
    note.update({'tags': ['.']})
    put('/note/2', note, cookies=cookies)

    describe('guest query')
    res = post('/query', {}).json()
    assert res['total'] == 10
    assert len(res['notes']) == 10

    describe('me query')
    res = post('/query', {}, cookies=cookies).json()
    assert res['total'] == 11
    assert len(res['notes']) == 11


def test_filter():
    db.getdb().note.remove({})

    post('/note', {'type': 'diary', 'content': '1'}, cookies=cookies)
    post('/note', {'type': 'diary', 'content': '2'}, cookies=cookies)
    post('/note', {'type': 'book'}, cookies=cookies)
    post('/note', {'type': 'blog'}, cookies=cookies)

    post('/note', {'tags': ['.', 'foo']}, cookies=cookies)
    post('/note', {'tags': ['foo', 'bar']}, cookies=cookies)
    post('/note', {'tags': ['baz']}, cookies=cookies)

    describe('query book type')
    res = post('/query', {'type': 'book'}).json()
    assert len(res['notes']) == 1

    describe('query diary type')
    res = post('/query', {'type': 'diary'}).json()
    assert len(res['notes']) == 2

    describe('guest query not include hidden')
    res = post('/query', {'tags': 'foo'}).json()
    assert len(res['notes']) == 1

    describe('me query include hidden')
    res = post('/query', {'tags': 'foo'}, cookies=cookies).json()
    assert len(res['notes']) == 2


test_basic()
test_hidden()
test_pagination()
test_filter()
