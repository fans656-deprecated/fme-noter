class Error(Exception):

    def __init__(self, message='bad request', status_code=400):
        self.resp = (message, status_code)


class InternalError(Error):

    def __init__(self):
        super(InternalError, self).__init__(
            'internal server error', 500
        )


class Unauthorized(Error):

    def __init__(self):
        super(Unauthorized, self).__init__(
            'unauthorized', 401
        )


class NotFound(Error):

    def __init__(self, res=''):
        super(NotFound, self).__init__(
            '{} not found'.format(res), 404
        )
