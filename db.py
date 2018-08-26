import pymongo


def getdb(g={}):
    if 'db' not in g:
        g['db'] = pymongo.MongoClient().noter
    return g['db']


if __name__ == '__main__':
    r = getdb().note.find({})
    for note in r:
        print note
