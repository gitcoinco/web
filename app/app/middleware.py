import bleach


def drop_accept_langauge(get_response):
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


def bleach_requests(get_response):
    """
    This middleware uses the bleach library to sanitize incoming requests to
    prevent XSS and injection attacks
    """

    def middleware(request):
        if request.method == 'POST':
            # make request mutable
            request.POST = request.POST.copy()
            for key in request.POST:
                request.POST[key] = bleach.clean(request.POST[key])

        response = get_response(request)

        return response

    return middleware
