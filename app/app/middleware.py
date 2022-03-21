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

def drop_recaptcha_post(get_response):
    """Define middleware to alter the request to act as a GET if the post data contains g-recaptcha-response

    This middleware allows us to ignore subsequent recaptcha submissions if the user has already passed
    the recaptcha in a different window.

    """

    def middleware(request):
        """Define middleware to set method to GET if g-recaptcha-response is present in POST dict."""
        if request.method == "POST" and "g-recaptcha-response" in request.POST:
            request.method = "GET"
            request.POST = {}

        return get_response(request)

    return middleware
