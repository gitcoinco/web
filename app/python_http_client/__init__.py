import os

from .client import Client  # noqa
from .exceptions import (  # noqa
    HTTPError,
    BadRequestsError,
    UnauthorizedError,
    ForbiddenError,
    NotFoundError,
    MethodNotAllowedError,
    PayloadTooLargeError,
    UnsupportedMediaTypeError,
    TooManyRequestsError,
    InternalServerError,
    ServiceUnavailableError,
    GatewayTimeoutError
)


dir_path = os.path.dirname(os.path.realpath(__file__))
if os.path.isfile(os.path.join(dir_path, 'VERSION.txt')):
    with open(os.path.join(dir_path, 'VERSION.txt')) as version_file:
        __version__ = version_file.read().strip()
