import db
import utils
import note_util


def query_notes(query, page=None, size=None):
    if not page:
        page = 1
    if not size:
        size = 20

    r = db.getdb().note.find(query, {'_id': False})
    total = r.count()
    r.sort('ctime', -1)
    r.skip((page - 1) * size).limit(size)
    return {
        'page': page,
        'size': size,
        'total': total,
        'notes': list(r),
    }


class Note(object):

    @staticmethod
    def get(note_id):
        note = db.getdb().note.find_one({'id': note_id}, {'_id': False})
        if note:
            return Note(note)

    @staticmethod
    def post(note):
        note = Note(note)
        note.create()
        if note.save():
            return note

    @staticmethod
    def query(query, page=None, size=None):
        return query_notes(query, page, size)

    def __init__(self, note):
        self.note = note

    @property
    def id(self):
        return self.note['id']

    @property
    def tags(self):
        return self.note.get('tags', [])

    @property
    def exists(self):
        return note_util.exists(self.id)

    @property
    def hidden(self):
        return '.' in self.tags

    def create(self):
        self.note['id'] = note_util.gen_id()
        if 'ctime' not in self.note:
            self.note['ctime'] = utils.utc_now_as_str()

    def save(self):
        self.note['mtime'] = utils.utc_now_as_str()
        return note_util.save(self.note)

    def delete(self):
        return note_util.delete(self.id)

    def __getitem__(self, key):
        return self.note[key]
