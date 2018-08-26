import view


endpoints = [
    ('GET', '/note/<int:note_id>', view.get_note),
    ('PUT', '/note/<int:note_id>', view.put_note),
    ('DELETE', '/note/<int:note_id>', view.delete_note),
    ('POST', '/note', view.post_note),
    ('POST', '/query', view.query_notes),
]
