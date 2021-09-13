import json


class HTTPError(Exception):
    """ Base of all other errors"""

    def __init__(self, *args):
        if len(args) == 4:
            self.status_code = args[0]
            self.reason = args[1]
            self.body = args[2]
            self.headers = args[3]
        else:
            self.status_code = args[0].code
            self.reason = args[0].reason
            self.body = args[0].read()
            self.headers = args[0].hdrs

    def __reduce__(self):
        return (
            HTTPError,
            (self.status_code, self.reason, self.body, self.headers)
        )

    @property
    def to_dict(self):
        """
        :return: dict of response error from the API
        """
        return json.loads(self.body.decode('utf-8'))


class BadRequestsError(HTTPError):
    pass


class UnauthorizedError(HTTPError):
    pass


class ForbiddenError(HTTPError):
    pass


class NotFoundError(HTTPError):
    pass


class MethodNotAllowedError(HTTPError):
    pass


class PayloadTooLargeError(HTTPError):
    pass


class UnsupportedMediaTypeError(HTTPError):
    pass


class TooManyRequestsError(HTTPError):
    pass


class InternalServerError(HTTPError):
    pass


class ServiceUnavailableError(HTTPError):
    pass


class GatewayTimeoutError(HTTPError):
    pass


err_dict = {
    400: BadRequestsError,
    401: UnauthorizedError,
    403: ForbiddenError,
    404: NotFoundError,
    405: MethodNotAllowedError,
    413: PayloadTooLargeError,
    415: UnsupportedMediaTypeError,
    429: TooManyRequestsError,
    500: InternalServerError,
    503: ServiceUnavailableError,
    504: GatewayTimeoutError
}


def handle_error(error):
    try:
        exc = err_dict[error.code](error)
    except KeyError:
        return HTTPError(error)
    return exc
