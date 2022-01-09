import bleach


def drop_accept_language(get_response):
    """Define the middleware to remove accept-language headers from requests.

    This middleware is essentially a hack to allow us to continue to use the
    standard Django LocaleMiddleware without modification, but simply disable
    the autodetection aspect based on the Accept-Language header.

    """

    def middleware(request):
        """Define the middleware method that removes the accept-language header."""
        if 'HTTP_ACCEPT_LANGUAGE' in request.META:
            del request.META['HTTP_ACCEPT_LANGUAGE']

        response = get_response(request)
        return response

    return middleware
