from flask import request

import utils
from note import Note
from errors import Error, NotFound, Unauthorized, InternalError


def get_note(note_id):
    note = Note.get(note_id)
    if not note:
        raise NotFound()
    visitor = utils.get_visitor()
    if note.hidden and not visitor.is_me:
        raise NotFound()
    return note.note


def query_notes():
    query = request.json or {}
    page = utils.to_int(request.args.get('page'), 1)
    if page < 1:
        page = 1
    size = utils.to_int(request.args.get('size'), 20)
    if size < 1:
        size = 20

    visitor = utils.get_visitor()
    if not visitor.is_me:
        # filter out hidden notes
        query.update({
            '$and': [dict(query), {'tags': {'$not': {'$eq': '.'}}}]
        })

    return Note.query(query, page=page, size=size)


@utils.require_me_login
def post_note():
    note = request.json
    if not note:
        raise Error('note required')
    note = Note.post(note)
    if note:
        return note.note


@utils.require_me_login
def put_note(note_id):
    data = request.json
    if not data:
        raise Error('note required')
    note = Note.get(note_id)
    if not note:
        raise NotFound()
    data.pop('id', None)
    note.note.update(data)
    if note.save():
        return note.note


@utils.require_me_login
def delete_note(note_id):
    note = Note.get(note_id)
    if not note:
        raise NotFound()
    note.delete()
