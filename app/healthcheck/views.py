from django.http import HttpResponse


def lbcheck(request):
    """Handle returning a 200 response if the app is "basically" operational."""
    return HttpResponse(status=200)
