import json
import datetime
import functools
import traceback

import jwt
from flask import request

import conf
from errors import Error, InternalError
from note_errors import NoteError


def guarded(viewfunc):
    @functools.wraps(viewfunc)
    def wrapped(*args, **kwargs):
        try:
            resp = viewfunc(*args, **kwargs)
            if not resp:
                return ''
            elif isinstance(resp, dict):
                return json.dumps(resp)
            else:
                return resp
        except NoteError as e:
            return e.__class__.__name__, 400
        except Error as e:
            return e.resp
        except Exception:
            traceback.print_exc()
            return InternalError().resp
    return wrapped


def require_me_login(viewfunc):
    @functools.wraps(viewfunc)
    def wrapped(*args, **kwargs):
        try:
            token = request.cookies.get('token')
            user = jwt.decode(token, conf.pubkey, algorithm='RS512')
            assert user['username'] == 'fans656'
        except Exception:
            return 'Unauthorized', 401
        return viewfunc(*args, **kwargs)
    return wrapped


def utc_now_as_str():
    return datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')


def to_int(s, default=0):
    try:
        return int(s)
    except Exception:
        return default


def get_visitor():
    try:
        token = request.cookies.get('token')
        user = jwt.decode(token, conf.pubkey, algorithm='RS512')
        return User(user)
    except Exception:
        return User({'username': ''})


class User(object):

    def __init__(self, data):
        self.username = data['username']
        self.is_me = self.username == 'fans656'
