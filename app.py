from flask import *

import conf
import utils
from endpoints import endpoints


app = Flask(__name__)


@app.after_request
def after_request(r):
    r.headers['Cache-Control'] = 'no-cache'
    return r


for method, path, viewfunc in endpoints:
    viewfunc = utils.guarded(viewfunc)
    app.route(path, methods=[method])(viewfunc)


if __name__ == '__main__':
    app.run(
        host=conf.host,
        port=conf.port,
        threaded=True,
        debug=conf.debugging,
    )
