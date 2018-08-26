import db

from note_errors import InvalidId


def get_max_note_id():
    notes = db.getdb().note.find({}).sort('id', -1).limit(1)
    notes = list(notes)
    if not notes:
        return 0
    note = notes[0]
    return note['id']


def gen_id():
    return get_max_note_id() + 1


def ensure_valid_id(note):
    try:
        note_id = note['id']
        if not isinstance(note_id, int):
            note['id'] = int(note_id)
        assert note['id'] > 0
    except Exception:
        raise InvalidId()


def save(note):
    data = {'_id': note['id']}
    data.update(note)
    r = db.getdb().note.update({'id': note['id']}, data, upsert=True)
    return r['n'] == 1


def delete(note_id):
    r = db.getdb().note.remove({'id': note_id})
    return r['n'] == 1


def exists(note_id):
    return db.getdb().note.find_one({'id': note_id}) is not None


if __name__ == '__main__':
    print get_max_note_id()
